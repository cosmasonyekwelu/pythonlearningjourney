# **Week 5 — Financial Programming Essentials**

## **Overview**

Week 5 focuses on mastering **financial data processing, analysis, and visualization**. You'll learn to work with real-time market data, perform financial calculations, analyze time series, and build comprehensive financial analytics tools. By the end of this week, you'll be able to create sophisticated stock analysis applications and portfolio tracking systems — essential skills for any financial developer or quant analyst.

---

## **Learning Objectives**

By the end of Week 5, you should be able to:

- Fetch and process real-time financial data from various APIs
- Create interactive financial dashboards and visualizations
- Perform advanced financial calculations using Pandas
- Calculate key portfolio performance metrics
- Analyze and model time series data
- Clean and preprocess financial datasets
- Build complete stock analysis applications

---

## **Detailed Table of Contents**

### **Day 29 — Real-time Data Updates**

**Focus:** Working with live market data and streaming updates

**Topics:**

- WebSocket connections for real-time data
- Streaming market data from various sources
- Implementing data refresh mechanisms
- Handling real-time price updates
- Building live tickers and price monitors
- Managing data streams efficiently
- Error handling and reconnection logic

**Key Code Example:**

```python
import websocket
import json
import threading

class RealTimeData:
    def __init__(self):
        self.ws = None
        self.prices = {}

    def on_message(self, ws, message):
        data = json.loads(message)
        if 'symbol' in data and 'price' in data:
            self.prices[data['symbol']] = data['price']
            print(f"Updated {data['symbol']}: ${data['price']}")

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    def on_open(self, ws):
        print("WebSocket connection established")
        # Subscribe to symbols
        subscribe_msg = {
            "type": "subscribe",
            "symbols": ["AAPL", "GOOGL", "MSFT"]
        }
        ws.send(json.dumps(subscribe_msg))

    def start(self, url):
        self.ws = websocket.WebSocketApp(url,
                                on_open=self.on_open,
                                on_message=self.on_message,
                                on_error=self.on_error,
                                on_close=self.on_close)
        self.ws.run_forever()

# Usage
rtd = RealTimeData()
threading.Thread(target=rtd.start, args=("wss://api.example.com/live",)).start()
```

**Mini Project:** Build a live cryptocurrency price tracker that updates every 5 seconds.

**Online Learning Resources:**

- [WebSocket Client Documentation](https://websocket-client.readthedocs.io/)
- [Real Python WebSockets Tutorial](https://realpython.com/python-websockets/)
- [Alpaca Market Data Streaming](https://alpaca.markets/docs/api-documentation/api-v2/market-data/streaming/)
- [Binance WebSocket API](https://binance-docs.github.io/apidocs/spot/en/#websocket-market-streams)

---

### **Day 30 — Data Visualization & Dashboards**

**Focus:** Creating interactive financial charts and dashboards

**Topics:**

- Matplotlib and Seaborn for static charts
- Plotly for interactive visualizations
- Building financial dashboards with Dash
- Candlestick charts and OHLC data
- Technical indicator visualization
- Real-time chart updates
- Dashboard layout and design principles

**Key Code Example:**

```python
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import pandas as pd

# Create candlestick chart
def create_candlestick(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df['datetime'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price'
    )])

    fig.update_layout(
        title='Stock Price Candlestick Chart',
        yaxis_title='Price ($)',
        xaxis_title='Date'
    )
    return fig

# Create Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Financial Dashboard", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='symbol-selector',
        options=[
            {'label': 'Apple', 'value': 'AAPL'},
            {'label': 'Google', 'value': 'GOOGL'},
            {'label': 'Microsoft', 'value': 'MSFT'}
        ],
        value='AAPL'
    ),
    dcc.Graph(id='price-chart'),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 1 minute
        n_intervals=0
    )
])

@app.callback(
    Output('price-chart', 'figure'),
    Input('symbol-selector', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_chart(symbol, n):
    # Fetch data based on symbol
    df = fetch_stock_data(symbol)
    return create_candlestick(df)

if __name__ == '__main__':
    app.run_server(debug=True)
```

**Mini Project:** Build an interactive dashboard showing multiple technical indicators.

**Online Learning Resources:**

- [Plotly Python Documentation](https://plotly.com/python/)
- [Dash Official Documentation](https://dash.plotly.com/)
- [Matplotlib Financial Charts](https://matplotlib.org/stable/api/finance_api.html)
- [Seaborn Statistical Visualization](https://seaborn.pydata.org/)
- [Real Python Data Visualization Guide](https://realpython.com/python-data-visualization/)

---

### **Day 31 — Pandas for Financial Data & Basic Financial Calculations**

**Focus:** Mastering Pandas for financial analysis and calculations

**Topics:**

- Pandas DataFrames for financial data
- Time series operations and resampling
- Calculating returns and volatility
- Moving averages and rolling statistics
- Portfolio return calculations
- Risk metrics and Sharpe ratio
- Correlation analysis

**Key Code Example:**

```python
import pandas as pd
import numpy as np
import yfinance as yf

# Fetch stock data
def analyze_stock(symbol, period='1y'):
    stock = yf.download(symbol, period=period)

    # Calculate daily returns
    stock['Daily Return'] = stock['Close'].pct_change()

    # Calculate moving averages
    stock['MA_20'] = stock['Close'].rolling(window=20).mean()
    stock['MA_50'] = stock['Close'].rolling(window=50).mean()

    # Calculate volatility (annualized)
    daily_volatility = stock['Daily Return'].std()
    annual_volatility = daily_volatility * np.sqrt(252)

    # Calculate Sharpe ratio (assuming risk-free rate = 0.02)
    excess_returns = stock['Daily Return'].mean() - 0.02/252
    sharpe_ratio = excess_returns / daily_volatility * np.sqrt(252)

    analysis = {
        'symbol': symbol,
        'current_price': stock['Close'].iloc[-1],
        'total_return': (stock['Close'].iloc[-1] / stock['Close'].iloc[0] - 1) * 100,
        'annual_volatility': annual_volatility * 100,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': calculate_max_drawdown(stock['Close'])
    }

    return stock, analysis

def calculate_max_drawdown(prices):
    cumulative = prices / prices.cummax()
    return (1 - cumulative.min()) * 100

# Usage
symbols = ['AAPL', 'GOOGL', 'MSFT']
portfolio_analysis = {}

for symbol in symbols:
    data, analysis = analyze_stock(symbol)
    portfolio_analysis[symbol] = analysis
    print(f"{symbol} Analysis:")
    for key, value in analysis.items():
        print(f"  {key}: {value:.2f}")
```

**Mini Project:** Create a portfolio analyzer that calculates key metrics for multiple stocks.

**Online Learning Resources:**

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Python for Data Analysis Book](https://wesmckinney.com/book/)
- [Real Python Pandas Tutorials](https://realpython.com/tutorials/pandas/)
- [QuantInsti Pandas for Trading](https://blog.quantinsti.com/pandas-tutorial/)

---

### **Day 32 — Market Data APIs & Portfolio Performance Metrics**

**Focus:** Integrating with financial APIs and calculating portfolio metrics

**Topics:**

- Yahoo Finance API (yfinance)
- Alpha Vantage API integration
- IEX Cloud and Polygon.io
- Portfolio return calculations
- Risk-adjusted performance metrics
- Drawdown analysis
- Benchmark comparison

**Key Code Example:**

```python
import yfinance as yf
import pandas as pd
import numpy as np
from alpha_vantage.fundamentaldata import FundamentalData
import requests

class PortfolioAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.fundamental_data = FundamentalData(key=api_key) if api_key else None

    def get_portfolio_returns(self, portfolio, start_date, end_date):
        """
        portfolio: dict of {symbol: weight}
        """
        returns_data = {}

        for symbol, weight in portfolio.items():
            try:
                stock = yf.download(symbol, start=start_date, end=end_date)
                returns = stock['Close'].pct_change().dropna()
                returns_data[symbol] = returns * weight
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")

        portfolio_returns = pd.DataFrame(returns_data).sum(axis=1)
        return portfolio_returns

    def calculate_metrics(self, portfolio_returns, benchmark_returns=None):
        metrics = {}

        # Total return
        metrics['total_return'] = (portfolio_returns + 1).prod() - 1

        # Annualized return
        metrics['annualized_return'] = (1 + metrics['total_return']) ** (252/len(portfolio_returns)) - 1

        # Volatility
        metrics['volatility'] = portfolio_returns.std() * np.sqrt(252)

        # Sharpe ratio (assuming risk-free rate 2%)
        risk_free_rate = 0.02
        excess_returns = metrics['annualized_return'] - risk_free_rate
        metrics['sharpe_ratio'] = excess_returns / metrics['volatility']

        # Maximum drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        metrics['max_drawdown'] = drawdown.min()

        # Alpha and Beta (if benchmark provided)
        if benchmark_returns is not None:
            covariance = portfolio_returns.cov(benchmark_returns)
            benchmark_variance = benchmark_returns.var()
            metrics['beta'] = covariance / benchmark_variance

            benchmark_return = (benchmark_returns + 1).prod() - 1
            metrics['alpha'] = metrics['total_return'] - (risk_free_rate + metrics['beta'] * (benchmark_return - risk_free_rate))

        return metrics

    def get_fundamental_data(self, symbol):
        """Get fundamental data from Alpha Vantage"""
        if not self.fundamental_data:
            return None

        try:
            # Get company overview
            overview, _ = self.fundamental_data.get_company_overview(symbol)
            return {
                'pe_ratio': float(overview.get('PERatio', 0)),
                'market_cap': float(overview.get('MarketCapitalization', 0)),
                'dividend_yield': float(overview.get('DividendYield', 0)),
                'profit_margin': float(overview.get('ProfitMargin', 0))
            }
        except Exception as e:
            print(f"Error fetching fundamental data: {e}")
            return None

# Usage
analyzer = PortfolioAnalyzer(api_key='YOUR_ALPHA_VANTAGE_KEY')
portfolio = {'AAPL': 0.4, 'GOOGL': 0.3, 'MSFT': 0.3}
returns = analyzer.get_portfolio_returns(portfolio, '2023-01-01', '2024-01-01')
metrics = analyzer.calculate_metrics(returns)

print("Portfolio Performance Metrics:")
for metric, value in metrics.items():
    print(f"{metric}: {value:.4f}")
```

**Mini Project:** Build a comprehensive portfolio analysis tool with fundamental data.

**Online Learning Resources:**

- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [Alpha Vantage Documentation](https://www.alphavantage.co/documentation/)
- [IEX Cloud Documentation](https://iexcloud.io/docs/api/)
- [Portfolio Performance Metrics Guide](https://www.investopedia.com/articles/08/performance-measure.asp)

---

### **Day 33 — Time Series Analysis**

**Focus:** Advanced time series analysis techniques for financial data

**Topics:**

- Stationarity and unit root tests
- Autocorrelation and partial autocorrelation
- ARIMA modeling
- GARCH models for volatility
- Seasonal decomposition
- Forecasting techniques
- Rolling predictions

**Key Code Example:**

```python
import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

class FinancialTimeSeries:
    def __init__(self, symbol, period='2y'):
        self.symbol = symbol
        self.data = yf.download(symbol, period=period)
        self.returns = self.data['Close'].pct_change().dropna()

    def test_stationarity(self, timeseries):
        """Augmented Dickey-Fuller test for stationarity"""
        result = adfuller(timeseries.dropna())
        print('ADF Statistic:', result[0])
        print('p-value:', result[1])
        print('Critical Values:')
        for key, value in result[4].items():
            print(f'\t{key}: {value}')

        return result[1] < 0.05  # Stationary if p-value < 0.05

    def decompose_series(self, series, model='additive', period=252):
        """Seasonal decomposition of time series"""
        decomposition = seasonal_decompose(series, model=model, period=period)

        fig, axes = plt.subplots(4, 1, figsize=(12, 10))
        decomposition.observed.plot(ax=axes[0], title='Observed')
        decomposition.trend.plot(ax=axes[1], title='Trend')
        decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
        decomposition.resid.plot(ax=axes[3], title='Residual')
        plt.tight_layout()

        return decomposition

    def fit_arima(self, series, order=(1,1,1)):
        """Fit ARIMA model to time series"""
        model = ARIMA(series, order=order)
        fitted_model = model.fit()
        print(fitted_model.summary())
        return fitted_model

    def forecast_volatility(self, returns, p=1, q=1):
        """Simple volatility forecasting using GARCH-like approach"""
        from arch import arch_model

        # Fit GARCH model
        model = arch_model(returns * 100, vol='Garch', p=p, q=q)
        fitted_model = model.fit(disp='off')

        # Forecast
        forecast = fitted_model.forecast(horizon=5)
        forecast_volatility = np.sqrt(forecast.variance.values[-1,:])

        return fitted_model, forecast_volatility

    def calculate_rolling_metrics(self, window=20):
        """Calculate rolling metrics"""
        rolling_volatility = self.returns.rolling(window=window).std() * np.sqrt(252)
        rolling_sharpe = self.returns.rolling(window=window).mean() / self.returns.rolling(window=window).std() * np.sqrt(252)

        return {
            'rolling_volatility': rolling_volatility,
            'rolling_sharpe': rolling_sharpe
        }

# Usage
ts_analyzer = FinancialTimeSeries('AAPL')

# Test stationarity
print("Testing stationarity of returns:")
is_stationary = ts_analyzer.test_stationarity(ts_analyzer.returns)

# Decompose series
decomposition = ts_analyzer.decompose_series(ts_analyzer.data['Close'])

# Fit ARIMA model
arima_model = ts_analyzer.fit_arima(ts_analyzer.data['Close'].dropna(), order=(2,1,2))

# Calculate rolling metrics
rolling_metrics = ts_analyzer.calculate_rolling_metrics()
```

**Mini Project:** Build a time series forecasting system for stock prices.

**Online Learning Resources:**

- [Statsmodels Time Series Analysis](https://www.statsmodels.org/stable/tsa.html)
- [ARCH Package Documentation](https://arch.readthedocs.io/)
- [Time Series Analysis with Python](https://machinelearningmastery.com/time-series-forecasting/)
- [Forecasting: Principles and Practice](https://otexts.com/fpp3/)

---

### **Day 34 — Data Cleaning & Preprocessing**

**Focus:** Preparing financial data for analysis and modeling

**Topics:**

- Handling missing data in time series
- Outlier detection and treatment
- Data normalization and standardization
- Feature engineering for financial data
- Resampling and alignment
- Data validation and quality checks
- Creating training datasets

**Key Code Example:**

```python
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy import stats

class FinancialDataPreprocessor:
    def __init__(self):
        self.scalers = {}

    def handle_missing_data(self, df, method='ffill'):
        """
        Handle missing data in financial time series
        Methods: 'ffill', 'bfill', 'interpolate', 'drop'
        """
        if method == 'ffill':
            return df.ffill().bfill()  # Forward then backward fill
        elif method == 'interpolate':
            return df.interpolate(method='time')
        elif method == 'drop':
            return df.dropna()
        else:
            return df.fillna(method=method)

    def detect_outliers(self, series, method='zscore', threshold=3):
        """
        Detect outliers using various methods
        """
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(series.dropna()))
            return z_scores > threshold
        elif method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            return (series < (Q1 - 1.5 * IQR)) | (series > (Q3 + 1.5 * IQR))
        elif method == 'modified_zscore':
            median = series.median()
            mad = np.median(np.abs(series - median))
            modified_z_scores = 0.6745 * (series - median) / mad
            return np.abs(modified_z_scores) > threshold

    def treat_outliers(self, series, method='cap', **kwargs):
        """
        Treat outliers using various methods
        """
        outliers = self.detect_outliers(series, **kwargs)

        if method == 'cap':
            # Cap outliers at specified percentiles
            lower_bound = series.quantile(0.05)
            upper_bound = series.quantile(0.95)
            treated = series.clip(lower=lower_bound, upper=upper_bound)
        elif method == 'remove':
            treated = series[~outliers]
        elif method == 'median':
            median_val = series.median()
            treated = series.copy()
            treated[outliers] = median_val

        return treated

    def create_technical_features(self, df, windows=[5, 10, 20, 50]):
        """
        Create technical indicators as features
        """
        features_df = df.copy()

        # Price-based features
        features_df['returns'] = df['Close'].pct_change()
        features_df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))

        # Moving averages
        for window in windows:
            features_df[f'MA_{window}'] = df['Close'].rolling(window=window).mean()
            features_df[f'Volatility_{window}'] = df['Close'].pct_change().rolling(window=window).std()

        # RSI
        features_df['RSI'] = self.calculate_rsi(df['Close'])

        # MACD
        features_df['MACD'] = self.calculate_macd(df['Close'])

        # Bollinger Bands
        features_df['BB_upper'], features_df['BB_lower'] = self.calculate_bollinger_bands(df['Close'])

        return features_df

    def calculate_rsi(self, prices, window=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd

    def calculate_bollinger_bands(self, prices, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band

    def scale_features(self, df, features, method='standard'):
        """
        Scale features for machine learning
        """
        scaled_df = df.copy()

        for feature in features:
            if method == 'standard':
                scaler = StandardScaler()
            elif method == 'minmax':
                scaler = MinMaxScaler()

            scaled_values = scaler.fit_transform(df[feature].values.reshape(-1, 1))
            scaled_df[f'{feature}_scaled'] = scaled_values.flatten()
            self.scalers[feature] = scaler

        return scaled_df

# Usage
preprocessor = FinancialDataPreprocessor()

# Fetch and clean data
symbols = ['AAPL', 'GOOGL', 'MSFT']
clean_data = {}

for symbol in symbols:
    raw_data = yf.download(symbol, period='1y')

    # Handle missing data
    clean_data[symbol] = preprocessor.handle_missing_data(raw_data)

    # Create technical features
    features_data = preprocessor.create_technical_features(clean_data[symbol])

    # Treat outliers in returns
    features_data['returns_clean'] = preprocessor.treat_outliers(
        features_data['returns'], method='cap'
    )

    # Scale features
    features_to_scale = ['returns_clean', 'MA_20', 'Volatility_20', 'RSI']
    scaled_data = preprocessor.scale_features(features_data, features_to_scale)

    clean_data[symbol] = scaled_data
```

**Mini Project:** Create a data preprocessing pipeline for multiple stocks.

**Online Learning Resources:**

- [Pandas Data Cleaning Guide](https://pandas.pydata.org/docs/getting_started/intro_tutorials/06_calculate_statistics.html)
- [Scikit-learn Preprocessing](https://scikit-learn.org/stable/modules/preprocessing.html)
- [Data Cleaning with Python](https://realpython.com/python-data-cleaning-numpy-pandas/)
- [Financial Data Preprocessing Techniques](https://towardsdatascience.com/financial-data-preprocessing-for-machine-learning-21c8669a12c8)

---

### **Day 35 Weekly Project: Stock Data Analyzer**

**Focus:** Building a comprehensive stock analysis application

**Project Description:** Create a **Stock Data Analyzer** that provides comprehensive analysis of stock data including technical indicators, fundamental analysis, and predictive insights. The application should allow users to compare multiple stocks, visualize data, and generate investment insights.

**Key Features:**

- Multi-stock data fetching and comparison
- Technical indicator calculations and visualization
- Fundamental data analysis
- Portfolio optimization suggestions
- Risk assessment and metrics
- Exportable analysis reports
- Interactive dashboard

**Implementation Steps:**

1. **Data Collection Module**

   - Integrate multiple data sources (Yahoo Finance, Alpha Vantage)
   - Real-time and historical data fetching
   - Data caching for performance

2. **Analysis Engine**

   - Technical analysis (RSI, MACD, Bollinger Bands)
   - Fundamental analysis (P/E ratios, dividends, growth)
   - Risk metrics calculation
   - Correlation analysis

3. **Visualization Dashboard**

   - Interactive charts with Plotly/Dash
   - Comparison tools
   - Performance metrics display

4. **Reporting System**
   - PDF report generation
   - Export to Excel/CSV
   - Email alerts for specific conditions

**Stretch Goals:**

- Machine learning-based price predictions
- Sentiment analysis integration from news
- Options chain analysis
- Backtesting framework for strategies

**Key Code Structure:**

```python
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output
import numpy as np

class StockDataAnalyzer:
    def __init__(self):
        self.data_cache = {}

    def analyze_stock(self, symbol, period='1y'):
        """Comprehensive stock analysis"""
        # Data collection
        stock_data = self.get_stock_data(symbol, period)

        # Technical analysis
        technicals = self.technical_analysis(stock_data)

        # Fundamental analysis
        fundamentals = self.fundamental_analysis(symbol)

        # Risk analysis
        risk_metrics = self.risk_analysis(stock_data)

        return {
            'symbol': symbol,
            'data': stock_data,
            'technical_indicators': technicals,
            'fundamental_metrics': fundamentals,
            'risk_metrics': risk_metrics
        }

    def compare_stocks(self, symbols, period='1y'):
        """Compare multiple stocks"""
        comparison = {}
        for symbol in symbols:
            comparison[symbol] = self.analyze_stock(symbol, period)

        # Calculate correlation matrix
        returns_data = pd.DataFrame()
        for symbol, analysis in comparison.items():
            returns_data[symbol] = analysis['data']['Close'].pct_change()

        correlation_matrix = returns_data.corr()

        return {
            'individual_analysis': comparison,
            'correlation_matrix': correlation_matrix
        }

# Dashboard implementation
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Stock Data Analyzer", style={'textAlign': 'center'}),

    dcc.Dropdown(
        id='stock-selector',
        options=[
            {'label': 'Apple', 'value': 'AAPL'},
            {'label': 'Google', 'value': 'GOOGL'},
            {'label': 'Microsoft', 'value': 'MSFT'},
            {'label': 'Amazon', 'value': 'AMZN'},
            {'label': 'Tesla', 'value': 'TSLA'}
        ],
        value=['AAPL', 'GOOGL'],
        multi=True
    ),

    dcc.DatePickerRange(
        id='date-range',
        start_date='2023-01-01',
        end_date='2024-01-01'
    ),

    dcc.Tabs([
        dcc.Tab(label='Price Chart', children=[
            dcc.Graph(id='price-chart')
        ]),
        dcc.Tab(label='Technical Analysis', children=[
            dcc.Graph(id='technical-chart')
        ]),
        dcc.Tab(label='Fundamental Analysis', children=[
            html.Div(id='fundamental-metrics')
        ]),
        dcc.Tab(label='Risk Analysis', children=[
            html.Div(id='risk-metrics')
        ])
    ])
])

@app.callback(
    [Output('price-chart', 'figure'),
     Output('technical-chart', 'figure'),
     Output('fundamental-metrics', 'children'),
     Output('risk-metrics', 'children')],
    [Input('stock-selector', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_dashboard(selected_stocks, start_date, end_date):
    analyzer = StockDataAnalyzer()
    comparison = analyzer.compare_stocks(selected_stocks)

    # Create price chart
    price_fig = go.Figure()
    for symbol in selected_stocks:
        data = comparison['individual_analysis'][symbol]['data']
        price_fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            name=symbol,
            mode='lines'
        ))

    # Update layout
    price_fig.update_layout(title='Stock Price Comparison')

    # Add more chart creation logic...

    return price_fig, technical_fig, fundamental_html, risk_html

if __name__ == '__main__':
    app.run_server(debug=True)
```

**Project Resources:**

- [yfinance Advanced Usage](https://pypi.org/project/yfinance/)
- [Plotly Dash Gallery](https://dash.gallery/Portal/)
- [Financial Analysis with Python](https://github.com/firmai/financial-machine-learning)
- [Quantitative Finance Resources](https://quantra.quantinsti.com/)

---

## **Tools & Libraries**

- **Data Collection:** yfinance, requests, websocket-client, alpha-vantage
- **Data Analysis:** Pandas, NumPy, SciPy, statsmodels
- **Visualization:** Matplotlib, Seaborn, Plotly, Dash
- **Technical Analysis:** TA-Lib, pandas-ta
- **Machine Learning:** scikit-learn, TensorFlow, PyTorch
- **Backtesting:** backtrader, zipline
- **Deployment:** Flask, Django, Docker

---

## **Additional Learning Platforms**

### **Comprehensive Courses:**

- [Coursera: Python and Statistics for Financial Analysis](https://www.coursera.org/learn/python-statistics-financial-analysis)
- [edX: Computational Investing](https://www.edx.org/learn/computational-investing)
- [QuantInsti: Algorithmic Trading](https://www.quantinsti.com/algorithmic-trading)

### **Community & Support:**

- [Stack Overflow - Quantitative Finance](https://stackoverflow.com/questions/tagged/quantitative-finance)
- [QuantConnect Forums](https://www.quantconnect.com/forum/)
- [Reddit: r/algotrading](https://www.reddit.com/r/algotrading/)
- [Reddit: r/quant](https://www.reddit.com/r/quant/)

### **Practice Platforms:**

- [QuantConnect](https://www.quantconnect.com/)
- [Backtrader Examples](https://www.backtrader.com/docu/)
- [Kaggle Financial Datasets](https://www.kaggle.com/datasets?tags=13204-Finance)

---

## **Expected Outcomes**

By the end of Week 5, you will:

- Build sophisticated financial data analysis applications
- Work with real-time market data streams
- Create interactive financial dashboards
- Perform comprehensive portfolio analysis
- Implement time series forecasting models
- Develop robust data preprocessing pipelines
- Have a complete stock analysis tool for personal use

---

**Next Week Preview:** Week 6 Networking & Security.
