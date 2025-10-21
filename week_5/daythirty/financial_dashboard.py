"""
Financial Dashboard with Dash
"""
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

app = dash.Dash(__name__)
app.title = "Financial Dashboard"

STOCK_SYMBOLS = [
    {'label': 'Apple Inc.', 'value': 'AAPL'},
    {'label': 'Google (Alphabet)', 'value': 'GOOGL'},
    {'label': 'Microsoft', 'value': 'MSFT'},
    {'label': 'Amazon', 'value': 'AMZN'},
    {'label': 'Tesla', 'value': 'TSLA'},
    {'label': 'NVIDIA', 'value': 'NVDA'}
]

app.layout = html.Div([
    html.H1("Financial Analytics Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Select Stock Symbol:"),
            dcc.Dropdown(
                id='symbol-selector',
                options=STOCK_SYMBOLS,
                value='AAPL'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Select Time Period:"),
            dcc.Dropdown(
                id='period-selector',
                options=[
                    {'label': '1 Month', 'value': '1mo'},
                    {'label': '3 Months', 'value': '3mo'},
                    {'label': '6 Months', 'value': '6mo'},
                    {'label': '1 Year', 'value': '1y'}
                ],
                value='6mo'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Chart Type:"),
            dcc.RadioItems(
                id='chart-type-selector',
                options=[
                    {'label': 'Candlestick', 'value': 'candlestick'},
                    {'label': 'Line', 'value': 'line'}
                ],
                value='candlestick'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'})
    ]),

    html.Div(id='key-metrics', style={'padding': '20px'}),

    dcc.Graph(id='price-chart'),

    dcc.Graph(id='technical-chart'),

    html.Div([
        html.Label("Stock Comparison:"),
        dcc.Dropdown(
            id='comparison-selector',
            options=STOCK_SYMBOLS,
            value=['AAPL', 'MSFT'],
            multi=True
        ),
        dcc.Graph(id='comparison-chart')
    ], style={'padding': '20px'}),

    dcc.Interval(
        id='interval-component',
        interval=300000,
        n_intervals=0
    )
])


def fetch_stock_data(symbol, period='6mo'):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            return pd.DataFrame()

        hist = hist.reset_index()
        hist['Symbol'] = symbol
        return hist
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()


def calculate_metrics(df):
    """Calculate key financial metrics"""
    if df.empty:
        return {}

    current_price = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
    day_change = current_price - prev_close
    day_change_pct = (day_change / prev_close) * 100

    return {
        'current_price': current_price,
        'day_change': day_change,
        'day_change_pct': day_change_pct
    }


@app.callback(
    Output('price-chart', 'figure'),
    Input('symbol-selector', 'value'),
    Input('period-selector', 'value'),
    Input('chart-type-selector', 'value')
)
def update_price_chart(symbol, period, chart_type):
    """Update the main price chart"""
    df = fetch_stock_data(symbol, period)

    if df.empty:
        return go.Figure()

    if chart_type == 'candlestick':
        fig = go.Figure(data=[go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        )])
    else:
        fig = go.Figure(data=[go.Scatter(
            x=df['Date'],
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        )])

    fig.update_layout(
        title=f'{symbol} Price Chart',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_white',
        height=400
    )

    return fig


@app.callback(
    Output('technical-chart', 'figure'),
    Input('symbol-selector', 'value'),
    Input('period-selector', 'value')
)
def update_technical_chart(symbol, period):
    """Update technical indicators chart"""
    df = fetch_stock_data(symbol, period)

    if df.empty:
        return go.Figure()

    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Close'], name='Close Price',
        line=dict(color='blue', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['SMA_20'], name='SMA 20',
        line=dict(color='orange', width=1, dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['SMA_50'], name='SMA 50',
        line=dict(color='red', width=1, dash='dash')
    ))

    fig.update_layout(
        title=f'{symbol} - Technical Indicators',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_white',
        height=400
    )

    return fig


@app.callback(
    Output('comparison-chart', 'figure'),
    Input('comparison-selector', 'value')
)
def update_comparison_chart(symbols):
    """Update stock comparison chart"""
    if not symbols:
        return go.Figure()

    fig = go.Figure()

    for symbol in symbols:
        df = fetch_stock_data(symbol, '6mo')
        if not df.empty:
            base_price = df['Close'].iloc[0]
            normalized_close = (df['Close'] / base_price - 1) * 100

            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=normalized_close,
                name=symbol,
                mode='lines'
            ))

    fig.update_layout(
        title='Stock Performance Comparison',
        yaxis_title='Percentage Change',
        xaxis_title='Date',
        template='plotly_white',
        height=400
    )

    return fig


@app.callback(
    Output('key-metrics', 'children'),
    Input('symbol-selector', 'value'),
    Input('period-selector', 'value')
)
def update_metrics(symbol, period):
    """Update key metrics display"""
    df = fetch_stock_data(symbol, period)
    metrics = calculate_metrics(df)

    if not metrics:
        return "No data available"

    change_color = 'green' if metrics['day_change'] >= 0 else 'red'
    change_icon = '▲' if metrics['day_change'] >= 0 else '▼'

    return html.Div([
        html.H3(f"{symbol} - ${metrics['current_price']:.2f}"),
        html.P(f"{change_icon} ${metrics['day_change']:.2f} ({metrics['day_change_pct']:.2f}%)",
               style={'color': change_color, 'fontSize': '20px'})
    ])


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
