"""
Static Charts with Matplotlib and Seaborn
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def create_line_chart(df):
    """Create a simple line chart for stock prices"""
    fig, ax = plt.subplots(figsize=(12, 6))

    for symbol in df['symbol'].unique():
        symbol_data = df[df['symbol'] == symbol]
        ax.plot(symbol_data['datetime'], symbol_data['close'],
                label=symbol, linewidth=2)

    ax.set_title('Stock Price Trends')
    ax.set_xlabel('Date')
    ax.set_ylabel('Closing Price')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def create_ohlc_chart(df, symbol='AAPL'):
    """Create OHLC chart using matplotlib"""
    symbol_data = df[df['symbol'] == symbol].copy()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Create OHLC bars
    for i, (idx, row) in enumerate(symbol_data.iterrows()):
        color = 'green' if row['close'] >= row['open'] else 'red'

        # High-Low line
        ax1.plot([i, i], [row['low'], row['high']], color='black', linewidth=1)

        # Open-Close rectangle
        height = row['close'] - row['open']
        ax1.bar(i, height, bottom=row['open'],
                color=color, alpha=0.7, width=0.6)

    ax1.set_title(f'{symbol} OHLC Chart')
    ax1.set_ylabel('Price')
    ax1.set_xticks(range(len(symbol_data)))
    ax1.set_xticklabels(symbol_data['datetime'].dt.strftime('%Y-%m-%d'))

    # Volume chart
    colors = ['green' if c >= o else 'red'
              for c, o in zip(symbol_data['close'], symbol_data['open'])]
    ax2.bar(range(len(symbol_data)),
            symbol_data['volume'], color=colors, alpha=0.7)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Volume')
    ax2.set_xticks(range(len(symbol_data)))
    ax2.set_xticklabels(symbol_data['datetime'].dt.strftime('%Y-%m-%d'))

    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def create_correlation_heatmap(df):
    """Create correlation heatmap for stock returns"""
    returns_data = []
    for symbol in df['symbol'].unique():
        symbol_data = df[df['symbol'] == symbol].sort_values('datetime')
        symbol_data['return'] = symbol_data['close'].pct_change()
        returns_data.append(symbol_data[['datetime', 'return']].rename(
            columns={'return': f'{symbol}_return'}))

    returns_df = returns_data[0]
    for ret_df in returns_data[1:]:
        returns_df = returns_df.merge(ret_df, on='datetime')

    corr_matrix = returns_df[[
        col for col in returns_df.columns if 'return' in col]].corr()

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, ax=ax)
    ax.set_title('Stock Returns Correlation Matrix')
    return fig


def create_technical_indicators_chart(df, symbol='AAPL'):
    """Create static chart with technical indicators"""
    symbol_data = df[df['symbol'] == symbol].copy()

    symbol_data['SMA_20'] = symbol_data['close'].rolling(window=2).mean()
    symbol_data['SMA_50'] = symbol_data['close'].rolling(window=3).mean()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    ax1.plot(symbol_data['datetime'], symbol_data['close'],
             label='Close Price', linewidth=2)
    ax1.plot(symbol_data['datetime'], symbol_data['SMA_20'],
             label='SMA 20', linestyle='--')
    ax1.plot(symbol_data['datetime'], symbol_data['SMA_50'],
             label='SMA 50', linestyle='--')
    ax1.set_title(f'{symbol} - Price and Moving Averages')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    colors = ['green' if c >= o else 'red'
              for c, o in zip(symbol_data['close'], symbol_data['open'])]
    ax2.bar(symbol_data['datetime'],
            symbol_data['volume'], color=colors, alpha=0.7)
    ax2.set_title('Volume')
    ax2.set_xlabel('Date')

    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    df = pd.read_csv('data/sample_stock_data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])

    line_chart = create_line_chart(df)
    plt.savefig('line_chart.png', dpi=300, bbox_inches='tight')

    ohlc_chart = create_ohlc_chart(df)
    plt.savefig('ohlc_chart.png', dpi=300, bbox_inches='tight')

    corr_heatmap = create_correlation_heatmap(df)
    plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')

    tech_chart = create_technical_indicators_chart(df)
    plt.savefig('technical_indicators.png', dpi=300, bbox_inches='tight')

    plt.show()
