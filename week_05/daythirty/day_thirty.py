"""
Python Learning Journey - Day Thirty
Topic: Financial Data Visualization & Dashboard Mastery
Date: October 21, 2025
Author: Cosmas Onyekwelu
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')


class FinancialVisualization:
    """
    Master class for financial data visualization techniques
    """

    def __init__(self):
        self.stock_data = None
        self.technical_data = None

    def generate_sample_data(self, days=100, symbols=['AAPL', 'GOOGL', 'MSFT']):
        """
        Generate realistic sample stock data for demonstration
        """
        dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
        data = []

        for symbol in symbols:
            # Start with realistic base prices
            if symbol == 'AAPL':
                base_price = 150
                volatility = 2.5
            elif symbol == 'GOOGL':
                base_price = 2800
                volatility = 50
            else:  # MSFT
                base_price = 300
                volatility = 4

            # Generate price data with random walk
            prices = [base_price]
            for i in range(1, days):
                change = np.random.normal(0, volatility)
                # Prevent negative prices
                new_price = max(10, prices[-1] + change)
                prices.append(new_price)

            # Create OHLC data from generated prices
            for i, date in enumerate(dates):
                open_price = prices[i]
                close_price = prices[i] + np.random.normal(0, volatility/2)
                high_price = max(open_price, close_price) + \
                    abs(np.random.normal(0, volatility/3))
                low_price = min(open_price, close_price) - \
                    abs(np.random.normal(0, volatility/3))
                volume = np.random.randint(1000000, 5000000)

                data.append({
                    'datetime': date,
                    'symbol': symbol,
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': volume
                })

        self.stock_data = pd.DataFrame(data)
        return self.stock_data

    def fetch_real_data(self, symbols=['AAPL', 'GOOGL', 'MSFT'], period='6mo'):
        """
        Fetch real stock data from Yahoo Finance
        """
        all_data = []

        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period=period)

                if not hist.empty:
                    hist = hist.reset_index()
                    hist['symbol'] = symbol
                    hist.rename(columns={
                        'Date': 'datetime',
                        'Open': 'open',
                        'High': 'high',
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    }, inplace=True)

                    all_data.append(
                        hist[['datetime', 'symbol', 'open', 'high', 'low', 'close', 'volume']])

            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")

        if all_data:
            self.stock_data = pd.concat(all_data, ignore_index=True)
        else:
            print("No data fetched, generating sample data instead")
            self.generate_sample_data()

        return self.stock_data


class StaticChartGenerator:
    """
    Generate static financial charts using Matplotlib and Seaborn
    """

    @staticmethod
    def create_performance_comparison(data):
        """
        Create performance comparison line chart
        """
        fig, ax = plt.subplots(figsize=(14, 8))

        for symbol in data['symbol'].unique():
            symbol_data = data[data['symbol'] ==
                               symbol].sort_values('datetime')
            # Calculate cumulative returns
            symbol_data = symbol_data.copy()
            symbol_data['cumulative_return'] = (
                symbol_data['close'] / symbol_data['close'].iloc[0] - 1) * 100

            ax.plot(symbol_data['datetime'], symbol_data['cumulative_return'],
                    label=symbol, linewidth=2.5, marker='o', markersize=4)

        ax.set_title('Stock Performance Comparison\nCumulative Returns Over Time',
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Cumulative Return (%)', fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

    @staticmethod
    def create_volume_analysis(data, symbol='AAPL'):
        """
        Create volume analysis with price overlay
        """
        symbol_data = data[data['symbol'] == symbol].sort_values('datetime')

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10),
                                       gridspec_kw={'height_ratios': [2, 1]})

        # Price chart
        ax1.plot(symbol_data['datetime'], symbol_data['close'],
                 color='blue', linewidth=2, label='Close Price')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.set_title(f'{symbol} - Price and Volume Analysis',
                      fontsize=16, fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        # Volume chart with color coding
        colors = ['green' if close >= open_price else 'red'
                  for close, open_price in zip(symbol_data['close'], symbol_data['open'])]
        ax2.bar(symbol_data['datetime'], symbol_data['volume'],
                color=colors, alpha=0.7, label='Volume')
        ax2.set_ylabel('Volume', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)

        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

    @staticmethod
    def create_correlation_matrix(data):
        """
        Create correlation matrix heatmap
        """
        # Calculate daily returns
        returns_data = []
        for symbol in data['symbol'].unique():
            symbol_data = data[data['symbol'] ==
                               symbol].sort_values('datetime')
            symbol_data = symbol_data.copy()
            symbol_data['daily_return'] = symbol_data['close'].pct_change()
            returns_data.append(
                symbol_data[['datetime', 'daily_return']].rename(
                    columns={'daily_return': f'{symbol}_return'})
            )

        # Merge returns
        returns_df = returns_data[0]
        for ret_df in returns_data[1:]:
            returns_df = returns_df.merge(ret_df, on='datetime')

        # Calculate correlation matrix
        corr_matrix = returns_df[[
            col for col in returns_df.columns if 'return' in col]].corr()

        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', center=0,
                    square=True, ax=ax, fmt='.3f', cbar_kws={'shrink': 0.8})

        ax.set_title('Daily Returns Correlation Matrix\nStock Relationship Analysis',
                     fontsize=16, fontweight='bold', pad=20)
        return fig


class InteractiveChartGenerator:
    """
    Generate interactive financial charts using Plotly
    """

    @staticmethod
    def create_advanced_candlestick(data, symbol='AAPL', show_volume=True):
        """
        Create advanced interactive candlestick chart
        """
        symbol_data = data[data['symbol'] == symbol].sort_values('datetime')

        if show_volume:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                vertical_spacing=0.1, subplot_titles=(f'{symbol} Price', 'Volume'),
                                row_heights=[0.7, 0.3])
        else:
            fig = go.Figure()

        # Candlestick chart
        candlestick = go.Candlestick(
            x=symbol_data['datetime'],
            open=symbol_data['open'],
            high=symbol_data['high'],
            low=symbol_data['low'],
            close=symbol_data['close'],
            name='Price'
        )

        if show_volume:
            fig.add_trace(candlestick, row=1, col=1)
        else:
            fig.add_trace(candlestick)

        # Volume bars
        if show_volume:
            colors = ['green' if close >= open_price else 'red'
                      for close, open_price in zip(symbol_data['close'], symbol_data['open'])]

            volume_bars = go.Bar(
                x=symbol_data['datetime'],
                y=symbol_data['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            )
            fig.add_trace(volume_bars, row=2, col=1)

        fig.update_layout(
            title=f'{symbol} - Advanced Candlestick Chart',
            yaxis_title='Price ($)',
            template='plotly_white',
            height=600,
            showlegend=True
        )

        # Add range selector
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )

        return fig

    @staticmethod
    def create_technical_analysis_dashboard(data, symbol='AAPL'):
        """
        Create comprehensive technical analysis dashboard
        """
        symbol_data = data[data['symbol'] ==
                           symbol].sort_values('datetime').copy()

        # Calculate technical indicators
        symbol_data['SMA_20'] = symbol_data['close'].rolling(window=20).mean()
        symbol_data['SMA_50'] = symbol_data['close'].rolling(window=50).mean()
        symbol_data['RSI'] = InteractiveChartGenerator.calculate_rsi(
            symbol_data['close'])
        symbol_data['MACD'], symbol_data['MACD_Signal'] = InteractiveChartGenerator.calculate_macd(
            symbol_data['close'])

        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(
                f'{symbol} - Price with Moving Averages',
                'Relative Strength Index (RSI)',
                'MACD Indicator',
                'Volume'
            ),
            row_heights=[0.35, 0.2, 0.2, 0.25]
        )

        # Price and moving averages
        fig.add_trace(go.Candlestick(
            x=symbol_data['datetime'],
            open=symbol_data['open'],
            high=symbol_data['high'],
            low=symbol_data['low'],
            close=symbol_data['close'],
            name='Price'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=symbol_data['datetime'], y=symbol_data['SMA_20'],
            name='SMA 20', line=dict(color='orange', width=1.5)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=symbol_data['datetime'], y=symbol_data['SMA_50'],
            name='SMA 50', line=dict(color='red', width=1.5)
        ), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(
            x=symbol_data['datetime'], y=symbol_data['RSI'],
            name='RSI', line=dict(color='purple', width=2)
        ), row=2, col=1)

        fig.add_hrect(y0=70, y1=100, line_width=0,
                      fillcolor="red", opacity=0.1, row=2, col=1)
        fig.add_hrect(y0=0, y1=30, line_width=0,
                      fillcolor="green", opacity=0.1, row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # MACD
        fig.add_trace(go.Scatter(
            x=symbol_data['datetime'], y=symbol_data['MACD'],
            name='MACD', line=dict(color='blue', width=2)
        ), row=3, col=1)

        fig.add_trace(go.Scatter(
            x=symbol_data['datetime'], y=symbol_data['MACD_Signal'],
            name='Signal Line', line=dict(color='red', width=1.5)
        ), row=3, col=1)

        # Volume
        colors = ['green' if close >= open_price else 'red'
                  for close, open_price in zip(symbol_data['close'], symbol_data['open'])]
        fig.add_trace(go.Bar(
            x=symbol_data['datetime'], y=symbol_data['volume'],
            name='Volume', marker_color=colors, opacity=0.7
        ), row=4, col=1)

        fig.update_layout(
            title=f'{symbol} - Comprehensive Technical Analysis Dashboard',
            height=900,
            showlegend=True,
            template='plotly_white'
        )

        fig.update_xaxes(rangeslider_visible=False)

        return fig

    @staticmethod
    def calculate_rsi(prices, window=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        return macd_line, signal_line


class PortfolioVisualizer:
    """
    Portfolio visualization and analysis tools
    """

    @staticmethod
    def create_portfolio_allocation(allocations):
        """
        Create portfolio allocation pie chart
        """
        fig = go.Figure(data=[go.Pie(
            labels=list(allocations.keys()),
            values=list(allocations.values()),
            hole=0.4,
            marker_colors=px.colors.qualitative.Set3
        )])

        fig.update_layout(
            title='Portfolio Allocation',
            template='plotly_white'
        )

        return fig

    @staticmethod
    def create_risk_return_scatter(data):
        """
        Create risk-return scatter plot for multiple stocks
        """
        risk_return_data = []

        for symbol in data['symbol'].unique():
            symbol_data = data[data['symbol'] ==
                               symbol].sort_values('datetime')
            returns = symbol_data['close'].pct_change().dropna()

            annual_return = returns.mean() * 252
            annual_risk = returns.std() * np.sqrt(252)

            risk_return_data.append({
                'symbol': symbol,
                'return': annual_return,
                'risk': annual_risk,
                'sharpe': annual_return / annual_risk if annual_risk > 0 else 0
            })

        risk_return_df = pd.DataFrame(risk_return_data)

        fig = px.scatter(risk_return_df, x='risk', y='return', text='symbol',
                         size='sharpe', color='sharpe',
                         title='Risk-Return Analysis of Stocks',
                         labels={'risk': 'Annual Risk (Std Dev)',
                                 'return': 'Annual Return',
                                 'sharpe': 'Sharpe Ratio'})

        fig.update_traces(textposition='top center')
        fig.update_layout(template='plotly_white', height=600)

        return fig


def run_comprehensive_demo():
    """
    Run a comprehensive demonstration of all visualization techniques
    """
    print("Day 30 - Financial Data Visualization Mastery")
    print("=" * 50)

    # Initialize visualization engine
    fv = FinancialVisualization()

    # Fetch or generate data
    print("1. Loading stock data...")
    try:
        data = fv.fetch_real_data(
            ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'], '3mo')
        print(f"   Real data loaded: {len(data)} records")
    except:
        data = fv.generate_sample_data(60, ['AAPL', 'GOOGL', 'MSFT', 'AMZN'])
        print(f"   Sample data generated: {len(data)} records")

    # Generate static charts
    print("2. Creating static charts...")
    static_gen = StaticChartGenerator()

    plt.figure(figsize=(15, 5))

    plt.subplot(131)
    performance_fig = static_gen.create_performance_comparison(data)
    plt.title('Static Chart 1: Performance Comparison')
    plt.axis('off')

    plt.subplot(132)
    volume_fig = static_gen.create_volume_analysis(data, 'AAPL')
    plt.title('Static Chart 2: Volume Analysis')
    plt.axis('off')

    plt.subplot(133)
    correlation_fig = static_gen.create_correlation_matrix(data)
    plt.title('Static Chart 3: Correlation Matrix')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

    # Generate interactive charts
    print("3. Creating interactive charts...")
    interactive_gen = InteractiveChartGenerator()

    # Candlestick chart
    candlestick_fig = interactive_gen.create_advanced_candlestick(data, 'AAPL')
    candlestick_fig.show()

    # Technical analysis dashboard
    technical_fig = interactive_gen.create_technical_analysis_dashboard(
        data, 'AAPL')
    technical_fig.show()

    # Portfolio visualizations
    print("4. Creating portfolio visualizations...")
    portfolio_vis = PortfolioVisualizer()

    # Portfolio allocation
    allocations = {'AAPL': 30, 'GOOGL': 25, 'MSFT': 20, 'AMZN': 15, 'TSLA': 10}
    allocation_fig = portfolio_vis.create_portfolio_allocation(allocations)
    allocation_fig.show()

    # Risk-return analysis
    risk_return_fig = portfolio_vis.create_risk_return_scatter(data)
    risk_return_fig.show()

    print("\nDemo completed successfully!")
    print("\nKey Learning Objectives Covered:")
    print("✓ Static charts with Matplotlib/Seaborn")
    print("✓ Interactive visualizations with Plotly")
    print("✓ Candlestick charts and OHLC data")
    print("✓ Technical indicator visualization")
    print("✓ Portfolio analysis tools")
    print("✓ Real-time data integration")
    print("✓ Dashboard design principles")


def learning_exercises():
    """
    Practical exercises for Day 30 learning
    """
    print("\nLearning Exercises")
    print("=" * 30)

    exercises = [
        "1. Modify the candlestick chart to add Bollinger Bands",
        "2. Create a function to calculate and visualize Fibonacci retracement levels",
        "3. Build a real-time dashboard that updates every 5 minutes",
        "4. Add volume profile analysis to the technical dashboard",
        "5. Create a sector rotation visualization using SPDR ETFs",
        "6. Implement a pairs trading correlation matrix",
        "7. Build an options chain visualization tool",
        "8. Create an earnings surprise visualization",
        "9. Implement market regime detection using volatility clusters",
        "10. Build an interactive economic calendar"
    ]

    for exercise in exercises:
        print(exercise)


if __name__ == "__main__":
    # Run the comprehensive demonstration
    run_comprehensive_demo()

    # Show learning exercises
    learning_exercises()

    print("\n" + "="*50)
    print("Day 30 Mastery Complete!")
    print("Next: Continue exploring advanced visualization techniques")
    print("and building more sophisticated financial dashboards.")
