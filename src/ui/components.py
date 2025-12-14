"""
Reusable UI components for Portfolio Watchdog.

This module provides custom Streamlit components for consistent
and improved UI/UX throughout the application.
"""

import streamlit as st


def status_badge(status: str, emoji: str) -> str:
    """
    Create a styled status badge with appropriate colors.

    Args:
        status: Status text ("GREEN", "YELLOW", "RED")
        emoji: Status emoji

    Returns:
        HTML string for styled badge
    """
    color_map = {
        "GREEN": "#10b981",  # Green-500
        "YELLOW": "#f59e0b",  # Amber-500
        "RED": "#ef4444",  # Red-500
    }
    color = color_map.get(status, "#6b7280")
    return f"""
    <div style="
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        background-color: {color}20;
        color: {color};
        font-weight: 600;
        font-size: 0.875rem;
        border: 1px solid {color}40;
    ">
        {emoji} {status}
    </div>
    """


def metric_card(title: str, value: str, delta: str = "", help_text: str = "") -> None:
    """
    Create a styled metric card.

    Args:
        title: Card title
        value: Main value to display
        delta: Optional delta/change indicator
        help_text: Optional help text
    """
    with st.container():
        st.metric(label=title, value=value, delta=delta, help=help_text)


def info_box(title: str, content: str, icon: str = "ℹ️") -> None:
    """
    Create a styled information box.

    Args:
        title: Box title
        content: Box content
        icon: Optional icon
    """
    st.info(f"**{icon} {title}**\n\n{content}")


def success_box(message: str) -> None:
    """Display a success message with better styling."""
    st.success(f"✅ {message}")


def error_box(message: str) -> None:
    """Display an error message with better styling."""
    st.error(f"❌ {message}")


def warning_box(message: str) -> None:
    """Display a warning message with better styling."""
    st.warning(f"⚠️ {message}")


def empty_state(icon: str, title: str, message: str, action_label: str = None) -> None:
    """
    Display an empty state with icon and message.

    Args:
        icon: Icon to display
        title: Empty state title
        message: Empty state message
        action_label: Optional action label
    """
    st.markdown(
        f"""
    <div class="empty-state" style="
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
        border-radius: 1rem;
        margin: 2rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    ">
        <div style="
            font-size: 5rem; 
            margin-bottom: 1.5rem;
            animation: bounce 2s infinite;
        ">{icon}</div>
        <h3 style="
            color: #1f2937; 
            margin-bottom: 0.75rem;
            font-size: 1.5rem;
            font-weight: 600;
        ">{title}</h3>
        <p style="
            color: #6b7280; 
            margin-bottom: 1.5rem;
            font-size: 1rem;
            max-width: 500px;
            margin-left: auto;
            margin-right: auto;
        ">{message}</p>
    </div>
    <style>
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def section_header(title: str, icon: str = "", description: str = "") -> None:
    """
    Create a styled section header.

    Args:
        title: Section title
        icon: Optional icon
        description: Optional description
    """
    st.markdown(
        f"""
    <div style="
        margin: 2rem 0 1rem 0;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e5e7eb;
    ">
        <h2 style="
            margin: 0;
            font-size: 1.75rem;
            font-weight: 600;
            color: #1f2937;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        ">
            {icon} {title}
        </h2>
        {f'<p style="color: #6b7280; margin-top: 0.5rem; margin-bottom: 0; font-size: 0.875rem;">{description}</p>' if description else ''}
    </div>
    """,
        unsafe_allow_html=True,
    )


def status_summary_card(green_count: int, yellow_count: int, red_count: int) -> None:
    """
    Display a summary card with status counts.

    Args:
        green_count: Number of green status tickers
        yellow_count: Number of yellow status tickers
        red_count: Number of red status tickers
    """
    total = green_count + yellow_count + red_count
    if total == 0:
        return

    # Calculate percentages
    green_pct = (green_count / total * 100) if total > 0 else 0
    yellow_pct = (yellow_count / total * 100) if total > 0 else 0
    red_pct = (red_count / total * 100) if total > 0 else 0

    # Create a more visual summary with progress bars
    st.markdown("### 📊 Portfolio Summary")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 1rem;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <div style="font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem;">Total</div>
                <div style="font-size: 2.5rem; font-weight: 700;">{total}</div>
                <div style="font-size: 0.75rem; opacity: 0.8;">Tickers</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                padding: 1.5rem;
                border-radius: 1rem;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <div style="font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem;">🟢 Healthy</div>
                <div style="font-size: 2.5rem; font-weight: 700;">{green_count}</div>
                <div style="font-size: 0.75rem; opacity: 0.8;">{green_pct:.0f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                padding: 1.5rem;
                border-radius: 1rem;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <div style="font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem;">🟡 Watch</div>
                <div style="font-size: 2.5rem; font-weight: 700;">{yellow_count}</div>
                <div style="font-size: 0.75rem; opacity: 0.8;">{yellow_pct:.0f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                padding: 1.5rem;
                border-radius: 1rem;
                color: white;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <div style="font-size: 0.875rem; opacity: 0.9; margin-bottom: 0.5rem;">🔴 Exit</div>
                <div style="font-size: 2.5rem; font-weight: 700;">{red_count}</div>
                <div style="font-size: 0.75rem; opacity: 0.8;">{red_pct:.0f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def apply_custom_css() -> None:
    """Apply custom CSS for improved styling."""
    st.markdown(
        """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global font improvements */
        html, body, [class*="st-"], p, div {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Main container improvements */
        .main > div {
            padding-top: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Better spacing for sections */
        .element-container {
            margin-bottom: 1.5rem;
        }
        
        /* Improved button styling with modern design */
        .stButton > button {
            border-radius: 0.75rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 600;
            padding: 0.5rem 1.5rem;
            border: none;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Primary button gradient */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
        }
        
        /* Better input styling */
        .stTextInput > div > div > input {
            border-radius: 0.75rem;
            border: 2px solid #e5e7eb;
            padding: 0.75rem 1rem;
            transition: all 0.2s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Improved selectbox styling */
        .stSelectbox > div > div > select {
            border-radius: 0.75rem;
            border: 2px solid #e5e7eb;
            padding: 0.75rem 1rem;
        }
        
        /* Improved table styling with better readability */
        .dataframe {
            border-radius: 0.75rem;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .dataframe thead th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            padding: 1rem;
        }
        
        .dataframe tbody tr {
            transition: background-color 0.2s ease;
        }
        
        .dataframe tbody tr:hover {
            background-color: #f9fafb;
        }
        
        /* Status badge styling */
        .status-badge {
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-weight: 600;
            display: inline-block;
            font-size: 0.875rem;
        }
        
        /* Better metric cards with enhanced styling */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        [data-testid="stMetricLabel"] {
            font-weight: 600;
            color: #6b7280;
            font-size: 0.875rem;
        }
        
        /* Enhanced metric containers */
        [data-testid="stMetricContainer"] {
            background: white;
            padding: 1.5rem;
            border-radius: 1rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        [data-testid="stMetricContainer"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
        }
        
        /* Sidebar improvements */
        .css-1d391kg {
            padding-top: 2rem;
            background: linear-gradient(180deg, #f9fafb 0%, #ffffff 100%);
        }
        
        /* Sidebar sections */
        .css-1lcbmhc {
            background: white;
            padding: 1rem;
            border-radius: 0.75rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Better spacing */
        .stMarkdown {
            margin-bottom: 1rem;
        }
        
        /* Improved title styling */
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }
        
        h2 {
            font-size: 1.75rem;
            font-weight: 600;
            color: #1f2937;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        
        h3 {
            font-size: 1.5rem;
            font-weight: 600;
            color: #374151;
        }
        
        /* Improved info/error/success boxes */
        .stAlert {
            border-radius: 0.75rem;
            border-left: 4px solid;
            padding: 1rem 1.5rem;
        }
        
        /* Better expander styling */
        .streamlit-expanderHeader {
            font-weight: 600;
            border-radius: 0.5rem;
        }
        
        /* Progress bar improvements */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 0.5rem;
        }
        
        /* Spinner improvements */
        .stSpinner > div {
            border-color: #667eea;
        }
        
        /* Improved divider */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
            margin: 2rem 0;
        }
        
        /* Better caption styling */
        .stCaption {
            color: #6b7280;
            font-size: 0.875rem;
        }
        
        /* Enhanced empty state */
        .empty-state {
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
            border-radius: 1rem;
            margin: 2rem 0;
        }
        
        /* Smooth animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .element-container {
            animation: fadeIn 0.3s ease-out;
        }
        
        /* Better scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def progress_bar_with_text(current: int, total: int, label: str = "") -> None:
    """
    Display a progress bar with text.

    Args:
        current: Current progress value
        total: Total value
        label: Optional label
    """
    if total == 0:
        return

    progress = current / total
    st.progress(progress)
    if label:
        st.caption(f"{label}: {current}/{total} ({progress * 100:.0f}%)")
