"""
Interactive Charts with Plotly
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def create_interactive_candlestick(df, symbol='AAPL'):
    """Create interactive candlestick chart"""
    symbol_data = df[df['symbol'] == symbol]

    fig = go.Figure(data=[go.Candlestick(
        x=symbol_data['datetime'],
        open=symbol_data['open'],
        high=symbol_data['high'],
        low=symbol_data['low'],
        close=symbol_data['close'],
        name='Price'
    )])

    fig.update_layout(
        title=f'{symbol} - Interactive Candlestick Chart',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_white',
        height=600
    )

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=5, label="5d", step="day", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    return fig


def create_technical_analysis_dashboard(df, symbol='AAPL'):
    """Create interactive dashboard with multiple technical indicators"""
    symbol_data = df[df['symbol'] == symbol].copy()

    symbol_data['SMA_20'] = symbol_data['close'].rolling(window=2).mean()
    symbol_data['SMA_50'] = symbol_data['close'].rolling(window=3).mean()
    symbol_data['RSI'] = calculate_rsi(symbol_data['close'])

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Price with Moving Averages', 'Volume', 'RSI'),
        row_heights=[0.5, 0.25, 0.25]
    )

    fig.add_trace(go.Candlestick(
        x=symbol_data['datetime'],
        open=symbol_data['open'],
        high=symbol_data['high'],
        low=symbol_data['low'],
        close=symbol_data['close'],
        name='Price'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=symbol_data['datetime'],
        y=symbol_data['SMA_20'],
        name='SMA 20',
        line=dict(color='orange', width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=symbol_data['datetime'],
        y=symbol_data['SMA_50'],
        name='SMA 50',
        line=dict(color='blue', width=2)
    ), row=1, col=1)

    colors = ['green' if close >= open else 'red'
              for close, open in zip(symbol_data['close'], symbol_data['open'])]
    fig.add_trace(go.Bar(
        x=symbol_data['datetime'],
        y=symbol_data['volume'],
        name='Volume',
        marker_color=colors,
        opacity=0.7
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=symbol_data['datetime'],
        y=symbol_data['RSI'],
        name='RSI',
        line=dict(color='purple', width=2)
    ), row=3, col=1)

    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(
        title=f'{symbol} - Technical Analysis Dashboard',
        height=800,
        showlegend=True,
        template='plotly_white'
    )

    fig.update_xaxes(rangeslider_visible=False)

    return fig


def create_comparison_chart(df):
    """Create comparison chart for multiple stocks"""
    fig = go.Figure()

    for symbol in df['symbol'].unique():
        symbol_data = df[df['symbol'] == symbol]
        base_price = symbol_data['close'].iloc[0]
        normalized_close = (symbol_data['close'] / base_price - 1) * 100

        fig.add_trace(go.Scatter(
            x=symbol_data['datetime'],
            y=normalized_close,
            name=symbol,
            mode='lines'
        ))

    fig.update_layout(
        title='Stock Performance Comparison',
        yaxis_title='Percentage Change',
        xaxis_title='Date',
        template='plotly_white',
        height=500
    )

    return fig


def calculate_rsi(prices, window=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


if __name__ == "__main__":
    df = pd.read_csv('data/sample_stock_data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])

    candlestick_fig = create_interactive_candlestick(df)
    candlestick_fig.write_html('interactive_candlestick.html')

    dashboard_fig = create_technical_analysis_dashboard(df)
    dashboard_fig.write_html('technical_dashboard.html')

    comparison_fig = create_comparison_chart(df)
    comparison_fig.write_html('comparison_chart.html')

    print("Interactive charts saved as HTML files")
