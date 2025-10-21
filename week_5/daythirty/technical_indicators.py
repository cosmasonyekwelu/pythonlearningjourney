"""
Technical Indicators Visualization
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class TechnicalIndicators:
    def __init__(self, df):
        self.df = df.copy()
        self.calculate_all_indicators()

    def calculate_all_indicators(self):
        """Calculate all technical indicators"""
        self.calculate_moving_averages()
        self.calculate_rsi()
        self.calculate_macd()
        self.calculate_bollinger_bands()

    def calculate_moving_averages(self):
        """Calculate various moving averages"""
        self.df['SMA_20'] = self.df['Close'].rolling(window=20).mean()
        self.df['SMA_50'] = self.df['Close'].rolling(window=50).mean()
        self.df['EMA_12'] = self.df['Close'].ewm(span=12).mean()
        self.df['EMA_26'] = self.df['Close'].ewm(span=26).mean()

    def calculate_rsi(self, window=14):
        """Calculate Relative Strength Index"""
        delta = self.df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        self.df['RSI'] = 100 - (100 / (1 + rs))

    def calculate_macd(self):
        """Calculate MACD indicator"""
        self.df['MACD'] = self.df['EMA_12'] - self.df['EMA_26']
        self.df['MACD_Signal'] = self.df['MACD'].ewm(span=9).mean()
        self.df['MACD_Histogram'] = self.df['MACD'] - self.df['MACD_Signal']

    def calculate_bollinger_bands(self, window=20, num_std=2):
        """Calculate Bollinger Bands"""
        self.df['BB_Middle'] = self.df['Close'].rolling(window=window).mean()
        bb_std = self.df['Close'].rolling(window=window).std()
        self.df['BB_Upper'] = self.df['BB_Middle'] + (bb_std * num_std)
        self.df['BB_Lower'] = self.df['BB_Middle'] - (bb_std * num_std)

    def create_comprehensive_chart(self, symbol):
        """Create comprehensive technical analysis chart"""
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price with Indicators', 'MACD',
                            'RSI', 'Bollinger Bands'),
            row_heights=[0.4, 0.2, 0.2, 0.2]
        )

        # Price and moving averages
        fig.add_trace(go.Candlestick(
            x=self.df['Date'],
            open=self.df['Open'],
            high=self.df['High'],
            low=self.df['Low'],
            close=self.df['Close'],
            name='Price'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=self.df['Date'], y=self.df['SMA_20'],
            name='SMA 20', line=dict(color='orange', width=1)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=self.df['Date'], y=self.df['SMA_50'],
            name='SMA 50', line=dict(color='red', width=1)
        ), row=1, col=1)

        # MACD
        fig.add_trace(go.Scatter(
            x=self.df['Date'], y=self.df['MACD'],
            name='MACD', line=dict(color='blue', width=2)
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=self.df['Date'], y=self.df['MACD_Signal'],
            name='Signal', line=dict(color='red', width=1)
        ), row=2, col=1)

        colors = ['green' if x >=
                  0 else 'red' for x in self.df['MACD_Histogram']]
        fig.add_trace(go.Bar(
            x=self.df['Date'], y=self.df['MACD_Histogram'],
            name='Histogram', marker_color=colors
        ), row=2, col=1)

        # RSI
        fig.add_trace(go.Scatter(
            x=self.df['Date'], y=self.df['RSI'],
            name='RSI', line=dict(color='purple', width=2)
        ), row=3, col=1)

        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

        # Bollinger Bands
        fig.add_trace(go.Scatter(
            x=self.df['Date'], y=self.df['Close'],
            name='Price', line=dict(color='blue', width=1)
        ), row=4, col=1)

        fig.add_trace(go.Scatter(
            x=self.df['Date'], y=self.df['BB_Upper'],
            name='Upper Band', line=dict(color='gray', width=1, dash='dash')
        ), row=4, col=1)

        fig.add_trace(go.Scatter(
            x=self.df['Date'], y=self.df['BB_Middle'],
            name='Middle Band', line=dict(color='black', width=1)
        ), row=4, col=1)

        fig.add_trace(go.Scatter(
            x=self.df['Date'], y=self.df['BB_Lower'],
            name='Lower Band', line=dict(color='gray', width=1, dash='dash')
        ), row=4, col=1)

        fig.update_layout(
            title=f'{symbol} - Comprehensive Technical Analysis',
            height=1000,
            showlegend=True,
            template='plotly_white'
        )

        return fig


def demo_technical_indicators():
    """Demo function to showcase technical indicators"""
    import yfinance as yf

    # Fetch sample data
    symbol = 'AAPL'
    stock = yf.Ticker(symbol)
    df = stock.history(period='6mo')
    df = df.reset_index()

    # Calculate indicators
    ti = TechnicalIndicators(df)

    # Create comprehensive chart
    fig = ti.create_comprehensive_chart(symbol)
    fig.write_html('comprehensive_technical_analysis.html')

    print("Comprehensive technical analysis chart saved")


if __name__ == "__main__":
    demo_technical_indicators()
