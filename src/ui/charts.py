"""
Dynamic chart components for Portfolio Watchdog.

This module provides interactive Plotly charts for visualizing stock data,
technical indicators, and price trends.
"""

from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.core.engine import fetch_ohlcv, compute_indicators


def create_price_chart(
    ticker: str,
    df: Optional[pd.DataFrame] = None,
    show_sma: bool = True,
    period: str = "6mo",
) -> go.Figure:
    """
    Create an interactive price chart with moving averages.

    Args:
        ticker: Stock ticker symbol
        df: Optional pre-fetched DataFrame (if None, fetches data)
        show_sma: Whether to show moving averages
        period: Time period for chart (default: 6 months)

    Returns:
        Plotly figure object
    """
    if df is None:
        df = fetch_ohlcv(ticker, period=period)

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Compute indicators if showing SMA
    if show_sma:
        df_ind = compute_indicators(df)

    fig = go.Figure()

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
            increasing_line_color="#10b981",
            decreasing_line_color="#ef4444",
        )
    )

    # Add moving averages
    if show_sma and "sma_200" in df_ind.columns:
        fig.add_trace(
            go.Scatter(
                x=df_ind.index,
                y=df_ind["sma_200"],
                name="200-day SMA",
                line=dict(color="#667eea", width=2, dash="dash"),
                opacity=0.7,
            )
        )

    if show_sma and "sma_50" in df_ind.columns:
        fig.add_trace(
            go.Scatter(
                x=df_ind.index,
                y=df_ind["sma_50"],
                name="50-day SMA",
                line=dict(color="#f59e0b", width=2, dash="dot"),
                opacity=0.7,
            )
        )

    # Update layout
    fig.update_layout(
        title=f"{ticker} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        template="plotly_white",
        hovermode="x unified",
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(rangeslider=dict(visible=False)),
        margin=dict(l=50, r=50, t=80, b=50),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    return fig


def create_volume_chart(ticker: str, df: Optional[pd.DataFrame] = None) -> go.Figure:
    """
    Create a volume chart.

    Args:
        ticker: Stock ticker symbol
        df: Optional pre-fetched DataFrame

    Returns:
        Plotly figure object
    """
    if df is None:
        df = fetch_ohlcv(ticker, period="6mo")

    if df.empty or "Volume" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="No volume data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    # Color bars based on price direction
    colors = []
    for i in range(len(df)):
        if i == 0:
            colors.append("#6b7280")
        else:
            if df["Close"].iloc[i] >= df["Close"].iloc[i - 1]:
                colors.append("#10b981")  # Green for up
            else:
                colors.append("#ef4444")  # Red for down

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
            marker_color=colors,
            opacity=0.7,
        )
    )

    fig.update_layout(
        title=f"{ticker} Trading Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        template="plotly_white",
        height=300,
        showlegend=False,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    return fig


def create_rsi_chart(ticker: str, df: Optional[pd.DataFrame] = None) -> go.Figure:
    """
    Create an RSI (Relative Strength Index) indicator chart.

    Args:
        ticker: Stock ticker symbol
        df: Optional pre-fetched DataFrame

    Returns:
        Plotly figure object
    """
    if df is None:
        df = fetch_ohlcv(ticker, period="6mo")

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    df_ind = compute_indicators(df)

    if "rsi_14" not in df_ind.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="RSI data not available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure()

    # Add RSI line
    fig.add_trace(
        go.Scatter(
            x=df_ind.index,
            y=df_ind["rsi_14"],
            name="RSI (14)",
            line=dict(color="#667eea", width=2),
            fill="tozeroy",
            fillcolor="rgba(102, 126, 234, 0.1)",
        )
    )

    # Add overbought/oversold lines
    fig.add_hline(
        y=70,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="Overbought (70)",
        annotation_position="right",
    )
    fig.add_hline(
        y=30,
        line_dash="dash",
        line_color="#10b981",
        annotation_text="Oversold (30)",
        annotation_position="right",
    )
    fig.add_hline(
        y=50,
        line_dash="dot",
        line_color="#6b7280",
        opacity=0.5,
    )

    fig.update_layout(
        title=f"{ticker} RSI Indicator",
        xaxis_title="Date",
        yaxis_title="RSI",
        yaxis=dict(range=[0, 100]),
        template="plotly_white",
        height=300,
        showlegend=True,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    return fig


def create_comprehensive_chart(
    ticker: str, df: Optional[pd.DataFrame] = None
) -> go.Figure:
    """
    Create a comprehensive chart with price, volume, and RSI in subplots.

    Args:
        ticker: Stock ticker symbol
        df: Optional pre-fetched DataFrame

    Returns:
        Plotly figure object with subplots
    """
    if df is None:
        df = fetch_ohlcv(ticker, period="6mo")

    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    df_ind = compute_indicators(df)

    # Create subplots: 3 rows (price, volume, RSI)
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=(
            f"{ticker} Price & Moving Averages",
            "Trading Volume",
            "RSI Indicator",
        ),
    )

    # Price candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
            increasing_line_color="#10b981",
            decreasing_line_color="#ef4444",
        ),
        row=1,
        col=1,
    )

    # Moving averages
    if "sma_200" in df_ind.columns:
        fig.add_trace(
            go.Scatter(
                x=df_ind.index,
                y=df_ind["sma_200"],
                name="200-day SMA",
                line=dict(color="#667eea", width=2, dash="dash"),
                opacity=0.7,
            ),
            row=1,
            col=1,
        )

    if "sma_50" in df_ind.columns:
        fig.add_trace(
            go.Scatter(
                x=df_ind.index,
                y=df_ind["sma_50"],
                name="50-day SMA",
                line=dict(color="#f59e0b", width=2, dash="dot"),
                opacity=0.7,
            ),
            row=1,
            col=1,
        )

    # Volume
    if "Volume" in df.columns:
        colors = []
        for i in range(len(df)):
            if i == 0:
                colors.append("#6b7280")
            else:
                colors.append(
                    "#10b981" if df["Close"].iloc[i] >= df["Close"].iloc[i - 1] else "#ef4444"
                )

        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["Volume"],
                name="Volume",
                marker_color=colors,
                opacity=0.7,
            ),
            row=2,
            col=1,
        )

    # RSI
    if "rsi_14" in df_ind.columns:
        fig.add_trace(
            go.Scatter(
                x=df_ind.index,
                y=df_ind["rsi_14"],
                name="RSI (14)",
                line=dict(color="#667eea", width=2),
                fill="tozeroy",
                fillcolor="rgba(102, 126, 234, 0.1)",
            ),
            row=3,
            col=1,
        )

        # RSI reference lines
        fig.add_hline(
            y=70,
            line_dash="dash",
            line_color="#ef4444",
            row=3,
            col=1,
        )
        fig.add_hline(
            y=30,
            line_dash="dash",
            line_color="#10b981",
            row=3,
            col=1,
        )

    # Update layout
    fig.update_layout(
        title=f"{ticker} Comprehensive Analysis",
        template="plotly_white",
        height=800,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=50, t=100, b=50),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    # Update y-axis labels
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=3, col=1)

    return fig


def create_portfolio_overview_chart(
    tickers: list[str], prices: list[float], statuses: list[str]
) -> go.Figure:
    """
    Create a portfolio overview chart showing all tickers.

    Args:
        tickers: List of ticker symbols
        prices: List of current prices
        statuses: List of status strings (GREEN, YELLOW, RED)

    Returns:
        Plotly figure object
    """
    # Color mapping
    color_map = {
        "GREEN": "#10b981",
        "YELLOW": "#f59e0b",
        "RED": "#ef4444",
    }
    colors = [color_map.get(status.split()[0], "#6b7280") for status in statuses]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=tickers,
            y=prices,
            name="Current Price",
            marker_color=colors,
            text=[f"${p:.2f}" for p in prices],
            textposition="outside",
            opacity=0.8,
        )
    )

    fig.update_layout(
        title="Portfolio Overview",
        xaxis_title="Ticker",
        yaxis_title="Price ($)",
        template="plotly_white",
        height=400,
        showlegend=False,
        margin=dict(l=50, r=50, t=60, b=50),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    return fig

