"""
Interactive Dashboard for Stock Data Analyzer
"""

from data_collection import data_collector
from stock_data_analyzer import stock_analyzer
import dash
from dash import Dash, html, dcc, Input, Output, callback
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


# Initialize Dash app
app = Dash(__name__, external_stylesheets=[
           'https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.title = "Stock Data Analyzer"

# Available symbols
available_symbols = data_collector.get_available_symbols()

app.layout = html.Div([
    html.H1("Stock Data Analyzer Dashboard", style={
            'textAlign': 'center', 'marginBottom': 30}),

    # Controls
    html.Div([
        html.Div([
            html.Label("Select Stocks:"),
            dcc.Dropdown(
                id='stock-selector',
                options=[{'label': sym, 'value': sym}
                         for sym in available_symbols],
                value=['AAPL', 'MSFT', 'GOOGL'],
                multi=True,
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Time Period:"),
            dcc.Dropdown(
                id='period-selector',
                options=[
                    {'label': '1 Month', 'value': '1mo'},
                    {'label': '3 Months', 'value': '3mo'},
                    {'label': '6 Months', 'value': '6mo'},
                    {'label': '1 Year', 'value': '1y'},
                    {'label': '2 Years', 'value': '2y'}
                ],
                value='1y',
                style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ], style={'marginBottom': 20}),

    # Tabs
    dcc.Tabs([
        dcc.Tab(label='Price Comparison', children=[
            html.Div([
                dcc.Graph(id='price-chart'),
                dcc.Graph(id='returns-chart')
            ])
        ]),

        dcc.Tab(label='Technical Analysis', children=[
            html.Div([
                dcc.Dropdown(
                    id='tech-stock-selector',
                    options=[{'label': sym, 'value': sym}
                             for sym in available_symbols],
                    value='AAPL',
                    style={'width': '50%', 'margin': '10px'}
                ),
                dcc.Graph(id='technical-chart')
            ])
        ]),

        dcc.Tab(label='Fundamental Analysis', children=[
            html.Div([
                dcc.Dropdown(
                    id='fundamental-stock-selector',
                    options=[{'label': sym, 'value': sym}
                             for sym in available_symbols],
                    value='AAPL',
                    style={'width': '50%', 'margin': '10px'}
                ),
                html.Div(id='fundamental-metrics')
            ])
        ]),

        dcc.Tab(label='Risk Analysis', children=[
            html.Div([
                dcc.Graph(id='risk-chart'),
                html.Div(id='risk-metrics')
            ])
        ]),

        dcc.Tab(label='Portfolio Analysis', children=[
            html.Div([
                dcc.Graph(id='correlation-heatmap'),
                html.Div(id='portfolio-metrics')
            ])
        ])
    ]),

    # Loading component
    dcc.Loading(
        id="loading",
        type="circle",
        children=html.Div(id="loading-output")
    )
])


@app.callback(
    [Output('price-chart', 'figure'),
     Output('returns-chart', 'figure')],
    [Input('stock-selector', 'value'),
     Input('period-selector', 'value')]
)
def update_price_charts(selected_stocks, selected_period):
    """Update price and returns charts"""
    if not selected_stocks:
        return go.Figure(), go.Figure()

    # Get comparison data
    comparison = stock_analyzer.compare_stocks(
        selected_stocks, selected_period)

    if 'error' in comparison:
        return go.Figure(), go.Figure()

    # Price chart
    price_fig = go.Figure()
    for symbol in selected_stocks:
        if symbol in comparison['individual_analysis']:
            data = comparison['individual_analysis'][symbol]['data']
            price_fig.add_trace(go.Scatter(
                x=data.index,
                y=data['Close'],
                name=symbol,
                mode='lines'
            ))

    price_fig.update_layout(
        title='Stock Price Comparison',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        hovermode='x unified'
    )

    # Returns chart
    returns_fig = go.Figure()
    for symbol in selected_stocks:
        if symbol in comparison['individual_analysis']:
            data = comparison['individual_analysis'][symbol]['data']
            cumulative_returns = (1 + data['Daily_Return']).cumprod() - 1
            returns_fig.add_trace(go.Scatter(
                x=data.index,
                y=cumulative_returns,
                name=symbol,
                mode='lines'
            ))

    returns_fig.update_layout(
        title='Cumulative Returns Comparison',
        xaxis_title='Date',
        yaxis_title='Cumulative Return',
        hovermode='x unified'
    )

    return price_fig, returns_fig


@app.callback(
    Output('technical-chart', 'figure'),
    [Input('tech-stock-selector', 'value'),
     Input('period-selector', 'value')]
)
def update_technical_chart(selected_stock, selected_period):
    """Update technical analysis chart"""
    if not selected_stock:
        return go.Figure()

    analysis = stock_analyzer.analyze_stock(selected_stock, selected_period)

    if 'error' in analysis or analysis['data'].empty:
        return go.Figure()

    data = analysis['data']
    technicals = analysis['technical_indicators']

    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Price with Moving Averages', 'RSI', 'MACD'),
        row_heights=[0.5, 0.25, 0.25]
    )

    # Price and moving averages
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'], name='Close Price',
        line=dict(color='blue', width=2)
    ), row=1, col=1)

    # Add moving averages if available
    moving_averages = technicals.get('moving_averages', {})
    for ma_name, ma_value in moving_averages.items():
        if 'sma' in ma_name and ma_value is not None:
            # Simplified - would need full series in practice
            pass

    # RSI
    if 'rsi' in technicals and technicals['rsi'] is not None:
        # Simplified - would need full RSI series in practice
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # MACD
    macd = technicals.get('macd', {})
    if macd:
        # Simplified - would need full MACD series in practice
        pass

    fig.update_layout(height=600, showlegend=True)
    return fig


@app.callback(
    Output('fundamental-metrics', 'children'),
    [Input('fundamental-stock-selector', 'value')]
)
def update_fundamental_metrics(selected_stock):
    """Update fundamental metrics display"""
    if not selected_stock:
        return html.Div("Select a stock to see fundamental metrics")

    analysis = stock_analyzer.analyze_stock(selected_stock)

    if 'error' in analysis:
        return html.Div(f"Error: {analysis['error']}")

    fundamentals = analysis.get('fundamental_metrics', {})

    metrics_html = []
    for category, metrics in fundamentals.items():
        metrics_html.append(html.H4(category.title()))

        for metric, value in metrics.items():
            if value != 'N/A':
                metrics_html.append(
                    html.P(f"{metric.replace('_', ' ').title()}: {value}"))

        metrics_html.append(html.Hr())

    return html.Div(metrics_html)


@app.callback(
    [Output('risk-chart', 'figure'),
     Output('risk-metrics', 'children')],
    [Input('stock-selector', 'value'),
     Input('period-selector', 'value')]
)
def update_risk_analysis(selected_stocks, selected_period):
    """Update risk analysis"""
    if not selected_stocks:
        return go.Figure(), html.Div()

    comparison = stock_analyzer.compare_stocks(
        selected_stocks, selected_period)

    if 'error' in comparison:
        return go.Figure(), html.Div()

    # Risk metrics table
    risk_data = []
    for symbol in selected_stocks:
        if symbol in comparison['individual_analysis']:
            risk_metrics = comparison['individual_analysis'][symbol]['risk_metrics']
            risk_data.append({
                'Symbol': symbol,
                'Volatility': f"{risk_metrics.get('volatility', 0):.3f}",
                'Sharpe Ratio': f"{risk_metrics.get('sharpe_ratio', 0):.3f}",
                'Max Drawdown': f"{risk_metrics.get('max_drawdown', 0):.3f}",
                'Win Rate': f"{risk_metrics.get('win_rate', 0):.3f}"
            })

    risk_df = pd.DataFrame(risk_data)

    # Create risk comparison chart
    risk_fig = go.Figure()

    for metric in ['volatility', 'sharpe_ratio']:
        values = []
        symbols = []
        for symbol in selected_stocks:
            if symbol in comparison['individual_analysis']:
                risk_metrics = comparison['individual_analysis'][symbol]['risk_metrics']
                values.append(risk_metrics.get(metric, 0))
                symbols.append(symbol)

        risk_fig.add_trace(go.Bar(
            x=symbols,
            y=values,
            name=metric.replace('_', ' ').title()
        ))

    risk_fig.update_layout(
        title='Risk Metrics Comparison',
        barmode='group'
    )

    # Create metrics table
    metrics_table = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in risk_df.columns])),
        html.Tbody([
            html.Tr([html.Td(risk_df.iloc[i][col]) for col in risk_df.columns])
            for i in range(len(risk_df))
        ])
    ], style={'margin': '20px'})

    return risk_fig, metrics_table


@app.callback(
    [Output('correlation-heatmap', 'figure'),
     Output('portfolio-metrics', 'children')],
    [Input('stock-selector', 'value'),
     Input('period-selector', 'value')]
)
def update_portfolio_analysis(selected_stocks, selected_period):
    """Update portfolio analysis"""
    if not selected_stocks or len(selected_stocks) < 2:
        return go.Figure(), html.Div("Select at least 2 stocks for portfolio analysis")

    comparison = stock_analyzer.compare_stocks(
        selected_stocks, selected_period)

    if 'error' in comparison:
        return go.Figure(), html.Div(f"Error: {comparison['error']}")

    # Correlation heatmap
    correlation_matrix = comparison['portfolio_analysis']['correlation_matrix']

    heatmap_fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale='RdBu',
        zmid=0
    ))

    heatmap_fig.update_layout(
        title='Stock Correlation Matrix',
        xaxis_title='Stocks',
        yaxis_title='Stocks'
    )

    # Portfolio metrics
    portfolio_risk = comparison['portfolio_analysis']['portfolio_risk']

    metrics_html = [
        html.H4("Portfolio Risk Metrics"),
        html.P(
            f"Portfolio Volatility: {portfolio_risk.get('volatility', 0):.3f}"),
        html.P(
            f"Portfolio Sharpe Ratio: {portfolio_risk.get('sharpe_ratio', 0):.3f}"),
        html.P(
            f"Maximum Drawdown: {portfolio_risk.get('max_drawdown', 0):.3f}"),
        html.P(
            f"Average Correlation: {comparison['portfolio_analysis']['diversification_metrics'].get('average_correlation', 0):.3f}")
    ]

    return heatmap_fig, html.Div(metrics_html)


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
