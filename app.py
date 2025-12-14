"""
Portfolio Watchdog Streamlit Application.

This is the main Streamlit dashboard that provides:
- Secure user authentication via streamlit-authenticator
- Watchlist management (add/remove tickers)
- Real-time traffic light status display for all watchlist tickers
- Actionable notes for each ticker based on technical analysis

The application connects to PostgreSQL for user and watchlist persistence,
and uses the engine.py module to perform technical analysis.
"""

import datetime as dt
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from src.utils.cache import clear_all_caches, get_cache_stats
from src.database.models import (
    SessionLocal,
    init_db,
    get_or_create_user,
    add_ticker_to_watchlist,
    remove_ticker_from_watchlist,
    get_watchlist_for_user,
)
from src.core.engine import classify_ticker
from src.ui.components import (
    apply_custom_css,
    empty_state,
    error_box,
    section_header,
    status_summary_card,
    success_box,
    warning_box,
)
from src.ui.charts import (
    create_price_chart,
    create_volume_chart,
    create_rsi_chart,
    create_comprehensive_chart,
    create_portfolio_overview_chart,
)

# Database initialization is now lazy - only happens when needed
# This prevents connection errors at import time


def load_auth_config(path: str = "config.yaml") -> dict:
    """
    Load YAML configuration for streamlit-authenticator.

    The config file contains:
    - User credentials (username, email, hashed password)
    - Cookie settings for session management
    - Pre-authorized email addresses (optional)

    Args:
        path: Path to the YAML configuration file

    Returns:
        Dictionary containing authentication configuration
    """
    with open(path, "r") as f:
        config = yaml.load(f, Loader=SafeLoader)
    return config


def build_authenticator(config: dict) -> stauth.Authenticate:
    """
    Initialize streamlit-authenticator object using config file.

    This creates the authentication handler that manages user login,
    session cookies, and logout functionality.

    Args:
        config: Dictionary containing authentication configuration

    Returns:
        Authenticate object for managing user sessions
    """
    credentials = config["credentials"]
    cookie_name = config["cookie"]["name"]
    cookie_key = config["cookie"]["key"]
    expiry_days = config["cookie"]["expiry_days"]

    authenticator = stauth.Authenticate(
        credentials,
        cookie_name,
        cookie_key,
        expiry_days,
    )
    return authenticator


def main() -> None:
    """
    Main Streamlit application function.

    Provides:
    - Secure login using streamlit-authenticator
    - Watchlist management for logged-in users
    - Portfolio Watchdog table with traffic light status and notes

    The application flow:
    1. User logs in via streamlit-authenticator
    2. User record is created/retrieved in PostgreSQL
    3. User can add/remove tickers from their watchlist
    4. Dashboard displays real-time traffic light status for all watchlist tickers
    """
    st.set_page_config(
        page_title="Portfolio Watchdog",
        page_icon="🚦",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": "Portfolio Watchdog - Automated Stock Analysis Dashboard",
        },
    )

    # Apply custom CSS for improved styling
    apply_custom_css()

    # Load authentication config from environment or default file
    # This allows deployment flexibility (e.g., different configs for dev/prod)
    config_path = os.getenv("AUTH_CONFIG_PATH", "config.yaml")

    # Check if config file exists
    if not os.path.exists(config_path):
        st.error(f"Authentication config file not found: {config_path}")
        st.info(
            "Please copy config_example.yaml to config.yaml and configure your users."
        )
        return

    try:
        config = load_auth_config(config_path)
        authenticator = build_authenticator(config)
    except Exception as e:
        st.error(f"Failed to load authentication config: {e}")
        return

    # Login form - displayed if user is not authenticated
    # Note: New API - login() renders the widget and uses session state
    authenticator.login(location="main", key="Login")

    # Access authentication status from session state (new API uses session state)
    # The authenticator stores status in session state after login() is called
    auth_status = st.session_state.get("authentication_status", False)
    if auth_status:
        # User is authenticated - show main dashboard
        authenticator.logout(button_name="Logout", location="sidebar")

        # Enhanced sidebar
        st.sidebar.markdown("---")
        name = st.session_state.get("name", "User")
        username = st.session_state.get("username", "unknown")
        st.sidebar.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 0.75rem;
                color: white;
                margin-bottom: 1rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">
                    👤 Welcome, {name}!
                </div>
                <div style="font-size: 0.875rem; opacity: 0.9;">
                    @{username}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("---")

        # Sidebar quick stats
        with st.sidebar:
            st.markdown(
                """
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 0.75rem;
                    margin-bottom: 1rem;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                ">
                    <h3 style="margin: 0 0 1rem 0; font-size: 1rem; font-weight: 600; color: #1f2937;">
                        📊 Quick Stats
                    </h3>
                </div>
                """,
                unsafe_allow_html=True,
            )
            cache_stats = get_cache_stats()
            total_cache = cache_stats.get("data_cache_size", 0) + cache_stats.get(
                "classification_cache_size", 0
            )
            st.metric("Cache Items", total_cache)
            st.caption("Cached data for faster loading")
            st.markdown("---")

        # Initialize database on first use (lazy initialization)
        try:
            init_db()
        except Exception as e:
            error_box(
                f"Database connection failed: {str(e)}\n\n"
                "Please configure your database:\n"
                "1. Set DATABASE_URL environment variable, or\n"
                "2. Use SQLite (default): The app will create portfolio_watchdog.db automatically"
            )
            st.info(
                "💡 **Quick Start**: The app will use SQLite by default. "
                "No PostgreSQL setup required for development!"
            )
            return

        # Ensure DB user record exists for this username
        # This syncs streamlit-authenticator identity with database
        db = SessionLocal()
        try:
            username = st.session_state.get("username", "unknown")
            user_creds = config["credentials"]["usernames"].get(username, {})
            user_email = user_creds.get("email")
            user = get_or_create_user(db, username=username, email=user_email)
        except Exception as e:
            error_box(f"Database error: {str(e)}")
            db.close()
            return

        # Main dashboard header with better styling
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 1rem;
                margin-bottom: 2rem;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: 700;">
                            🚦 Portfolio Watchdog
                        </h1>
                        <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">
                            Automated technical analysis dashboard for stock market monitoring
                        </p>
                    </div>
                    <div style="text-align: right; color: rgba(255, 255, 255, 0.9);">
                        <div style="font-size: 0.875rem; margin-bottom: 0.25rem;">🕐 Last updated</div>
                        <div style="font-size: 1rem; font-weight: 600;">
            """ + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ---- Watchlist: Add ticker ----
        section_header(
            "Add Ticker to Watchlist",
            "📊",
            "Enter a stock ticker symbol to add it to your watchlist",
        )

        # Improved add ticker form
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_ticker = st.text_input(
                    "Ticker Symbol",
                    value="",
                    max_chars=12,
                    key="new_ticker_input",
                    placeholder="e.g., TSLA, AAPL, MSFT, GOOGL",
                    help="Enter a valid stock ticker symbol (uppercase recommended)",
                )
            with col2:
                st.write("")  # Spacing
                add_button = st.button(
                    "➕ Add", type="primary", use_container_width=True
                )
            with col3:
                st.write("")  # Spacing
                if st.button("📋 Popular", use_container_width=True):
                    st.session_state.show_popular = True

            # Handle popular tickers
            if st.session_state.get("show_popular", False):
                popular_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
                st.info("💡 Quick add popular tickers:")
                pop_cols = st.columns(len(popular_tickers))
                for idx, ticker in enumerate(popular_tickers):
                    with pop_cols[idx]:
                        if st.button(
                            ticker, key=f"pop_{ticker}", use_container_width=True
                        ):
                            add_ticker_to_watchlist(db, user, ticker)
                            success_box(f"Added {ticker} to watchlist")
                            st.balloons()
                            st.rerun()

            if add_button:
                if new_ticker.strip():
                    try:
                        add_ticker_to_watchlist(db, user, new_ticker.strip().upper())
                        success_box(f"Added {new_ticker.upper()} to watchlist")
                        st.balloons()  # Celebration effect
                        st.rerun()
                    except Exception as e:
                        error_box(f"Failed to add ticker: {str(e)}")
                else:
                    warning_box("Please enter a valid ticker symbol")

        st.markdown("---")

        # ---- Display and manage watchlist ----
        watchlist = get_watchlist_for_user(db, user)

        if not watchlist:
            empty_state(
                "📋",
                "Your Watchlist is Empty",
                "Add tickers above to start monitoring your portfolio",
                "Add Ticker",
            )
        else:
            section_header(
                "Your Watchlist",
                "📋",
                f"Monitoring {len(watchlist)} ticker{'s' if len(watchlist) != 1 else ''}",
            )
            # Improved ticker management
            with st.expander("🗑️ Manage Watchlist", expanded=False):
                remove_col1, remove_col2 = st.columns([3, 1])
                with remove_col1:
                    ticker_to_remove = st.selectbox(
                        "Select ticker to remove",
                        options=[""] + sorted(watchlist),
                        key="remove_ticker_select",
                        help="Choose a ticker to remove from your watchlist",
                    )
                with remove_col2:
                    st.write("")  # Spacing
                    if st.button(
                        "🗑️ Remove", use_container_width=True, type="secondary"
                    ):
                        if ticker_to_remove:
                            try:
                                remove_ticker_from_watchlist(db, user, ticker_to_remove)
                                success_box(
                                    f"Removed {ticker_to_remove} from watchlist"
                                )
                                st.rerun()
                            except Exception as e:
                                error_box(f"Failed to remove ticker: {str(e)}")
                        else:
                            warning_box("Please select a ticker to remove")

            st.markdown("---")

            # Display portfolio status table
            if watchlist:
                section_header(
                    "Portfolio Status",
                    "🚦",
                    "Real-time technical analysis for all watchlist tickers",
                )

                # Show loading spinner while fetching data
                progress_placeholder = st.empty()
                try:
                    with st.spinner("🔍 Analyzing tickers and computing indicators..."):
                        progress_placeholder.progress(0)
                        now_str = dt.datetime.now(dt.timezone.utc).strftime(
                            "%Y-%m-%d %H:%M"
                        )

                        def _classify_ticker_safe(ticker: str) -> dict:
                            """Classify ticker and return row dict, handling errors."""
                            try:
                                result = classify_ticker(ticker)
                                return {
                                    "Ticker": result.ticker,
                                    "Price": f"${result.price:.2f}",
                                    "Status": f"{result.emoji} {result.status}",
                                    "AI Analysis": result.ai_commentary if result.ai_commentary else result.note,
                                    "Technical Note": result.note,
                                    "As Of": result.as_of.strftime("%Y-%m-%d %H:%M"),
                                }
                            except Exception as e:
                                return {
                                    "Ticker": ticker,
                                    "Price": "N/A",
                                    "Status": "❌ Error",
                                    "AI Analysis": f"Failed to classify: {str(e)[:100]}",
                                    "Technical Note": f"Error: {str(e)[:100]}",
                                    "As Of": now_str,
                                }

                        # Use parallel processing for multiple tickers (performance optimization)
                        sorted_tickers = sorted(watchlist)
                        max_workers = min(
                            len(sorted_tickers), 5
                        )  # Limit concurrent requests

                        # Progress tracking
                        total_tickers = len(sorted_tickers)
                        completed = 0

                        if len(sorted_tickers) > 1:
                            # Parallel execution for multiple tickers
                            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                                future_to_ticker = {
                                    executor.submit(_classify_ticker_safe, ticker): ticker
                                    for ticker in sorted_tickers
                                }
                                rows = []
                                for future in as_completed(future_to_ticker):
                                    rows.append(future.result())
                                    completed += 1
                                    progress_placeholder.progress(completed / total_tickers)
                        else:
                            # Single ticker - no need for threading overhead
                            rows = [_classify_ticker_safe(t) for t in sorted_tickers]
                            progress_placeholder.progress(1.0)

                        progress_placeholder.empty()

                        # Calculate summary statistics
                        green_count = sum(1 for r in rows if "🟢" in r.get("Status", ""))
                        yellow_count = sum(1 for r in rows if "🟡" in r.get("Status", ""))
                        red_count = sum(1 for r in rows if "🔴" in r.get("Status", ""))

                        # Display summary cards
                        if rows:
                            status_summary_card(green_count, yellow_count, red_count)
                            st.markdown("---")
                            
                            # Portfolio Overview Chart
                            try:
                                tickers_list = [r["Ticker"] for r in rows]
                                prices_list = [
                                    float(r["Price"].replace("$", "").replace(",", ""))
                                    if r["Price"] != "N/A"
                                    else 0.0
                                    for r in rows
                                ]
                                statuses_list = [r["Status"] for r in rows]
                                
                                if len(tickers_list) > 0 and all(p > 0 for p in prices_list):
                                    st.markdown("### 📈 Portfolio Overview")
                                    portfolio_fig = create_portfolio_overview_chart(
                                        tickers_list, prices_list, statuses_list
                                    )
                                    st.plotly_chart(portfolio_fig, use_container_width=True)
                                    st.markdown("---")
                            except Exception:
                                # Silently fail if chart creation fails
                                pass

                        # Display results in an improved table
                        df = pd.DataFrame(rows)

                        # Color-code rows based on status
                        def color_status(val):
                            if "🟢" in str(val):
                                return "background-color: #d1fae5; color: #065f46"
                            elif "🟡" in str(val):
                                return "background-color: #fef3c7; color: #92400e"
                            elif "🔴" in str(val):
                                return "background-color: #fee2e2; color: #991b1b"
                            elif "❌" in str(val):
                                return "background-color: #f3f4f6; color: #6b7280"
                            return ""

                        styled_df = df.style.map(color_status, subset=["Status"]).format(
                            {
                                "Price": lambda x: x if x == "N/A" else x,
                            }
                        )

                        st.dataframe(
                            styled_df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Ticker": st.column_config.TextColumn(
                                    "Ticker",
                                    width="small",
                                    help="Stock ticker symbol",
                                ),
                                "Price": st.column_config.TextColumn(
                                    "Price",
                                    width="small",
                                    help="Current closing price",
                                ),
                                "Status": st.column_config.TextColumn(
                                    "Status",
                                    width="medium",
                                    help="Traffic light status: 🟢 Green (Hold/Add), 🟡 Yellow (Watch), 🔴 Red (Exit)",
                                ),
                                "AI Analysis": st.column_config.TextColumn(
                                    "AI Analysis",
                                    width="large",
                                    help="AI-generated natural language explanation of the technical analysis",
                                ),
                                "Technical Note": st.column_config.TextColumn(
                                    "Technical Note",
                                    width="medium",
                                    help="Raw technical analysis indicators and signals",
                                ),
                                "As Of": st.column_config.TextColumn(
                                    "Last Updated",
                                    width="medium",
                                    help="Timestamp of the analysis",
                                ),
                            },
                        )
                        
                        # Individual Ticker Charts
                        st.markdown("---")
                        st.markdown("### 📊 Detailed Charts")
                        st.caption("Select a ticker to view detailed price charts and technical indicators")
                        
                        # Create tabs for different chart views
                        chart_tabs = st.tabs(["📈 Price Charts", "📊 Comprehensive View"])
                        
                        with chart_tabs[0]:
                            # Price charts for each ticker
                            selected_ticker = st.selectbox(
                                "Select ticker for detailed chart",
                                options=[""] + sorted(watchlist),
                                key="chart_ticker_select",
                                help="Choose a ticker to view its price chart",
                            )
                            
                            if selected_ticker:
                                try:
                                    col_chart1, col_chart2 = st.columns(2)
                                    
                                    with col_chart1:
                                        st.markdown(f"#### {selected_ticker} Price Chart")
                                        price_fig = create_price_chart(selected_ticker)
                                        st.plotly_chart(price_fig, use_container_width=True)
                                    
                                    with col_chart2:
                                        st.markdown(f"#### {selected_ticker} Volume")
                                        volume_fig = create_volume_chart(selected_ticker)
                                        st.plotly_chart(volume_fig, use_container_width=True)
                                    
                                    st.markdown(f"#### {selected_ticker} RSI Indicator")
                                    rsi_fig = create_rsi_chart(selected_ticker)
                                    st.plotly_chart(rsi_fig, use_container_width=True)
                                    
                                except Exception as e:
                                    error_box(f"Failed to load charts for {selected_ticker}: {str(e)[:100]}")
                        
                        with chart_tabs[1]:
                            # Comprehensive view
                            comp_ticker = st.selectbox(
                                "Select ticker for comprehensive analysis",
                                options=[""] + sorted(watchlist),
                                key="comp_ticker_select",
                                help="Choose a ticker to view comprehensive chart with price, volume, and RSI",
                            )
                            
                            if comp_ticker:
                                try:
                                    st.markdown(f"#### {comp_ticker} Comprehensive Analysis")
                                    comp_fig = create_comprehensive_chart(comp_ticker)
                                    st.plotly_chart(comp_fig, use_container_width=True)
                                except Exception as e:
                                    error_box(f"Failed to load comprehensive chart for {comp_ticker}: {str(e)[:100]}")

                        # Improved action bar
                        st.markdown("---")
                        col_refresh, col_cache, col_clear, col_info = st.columns([2, 1.5, 1, 1])
                        with col_refresh:
                            if st.button(
                                "🔄 Refresh Data", use_container_width=True, type="primary"
                            ):
                                st.rerun()
                        with col_cache:
                            cache_stats = get_cache_stats()
                            data_cache_size = cache_stats.get("data_cache_size", 0)
                            class_cache_size = cache_stats.get("classification_cache_size", 0)
                            total_cache = data_cache_size + class_cache_size
                            if total_cache > 0:
                                st.metric(
                                    "📊 Cache",
                                    f"{total_cache} items",
                                    help=f"Data: {data_cache_size} | Class: {class_cache_size}",
                                )
                            else:
                                st.caption("📊 Cache: Empty")
                        with col_clear:
                            if st.button("🗑️ Clear", use_container_width=True, type="secondary"):
                                clear_all_caches()
                                success_box("Cache cleared successfully!")
                                st.rerun()
                        with col_info:
                            if st.button("ℹ️ Help", use_container_width=True):
                                st.info(
                                    """
                                    **Traffic Light Status:**
                                    - 🟢 **GREEN**: Trend healthy, hold or add
                                    - 🟡 **YELLOW**: Correction zone, watch for entry
                                    - 🔴 **RED**: Structure broken, exit or avoid
                                    
                                    **Cache**: Speeds up repeated requests
                                    **Refresh**: Updates all ticker data
                                    """
                                )
                except Exception as e:
                    error_box(f"Error displaying portfolio status: {str(e)}")
                    st.exception(e)  # Show full error traceback

        db.close()

    elif st.session_state.get("authentication_status", None) is False:
        # Authentication failed - improved error display
        st.markdown("---")
        error_box("Username/password is incorrect. Please try again.")
        st.markdown("---")
    else:
        # Initial state - improved login prompt
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem 1rem;">
                <h1>🚦 Portfolio Watchdog</h1>
                <p style="color: #6b7280; font-size: 1.1rem;">
                    Automated Stock Analysis Dashboard
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.info(
            "👆 **Please log in** using the form above to access your portfolio dashboard."
        )


if __name__ == "__main__":
    main()
