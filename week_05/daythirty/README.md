# Day 30: Financial Data Visualization & Dashboards

**Date:** October 21, 2025

## Learning Objective
To master the art of financial data visualization using both static (Matplotlib/Seaborn) and interactive (Plotly) libraries.

## Concepts Covered
- **Static Charting**: Creating performance comparisons, volume bars, and correlation heatmaps.
- **Interactive Candlesticks**: Building OHLC charts with range sliders and hover details.
- **Technical Dashboards**: Visualizing multiple indicators (SMA, RSI, MACD) in a single synchronized layout.
- **Portfolio Analytics**: Creating pie charts for allocation and scatter plots for risk-return analysis.
- **Synthetic Data Generation**: Using random walks and normal distributions to simulate realistic stock behavior.

## Code Explanation
The `day_thirty.py` script is a visualization masterclass:
- **`StaticChartGenerator`**: Uses Matplotlib for traditional reporting graphics.
- **`InteractiveChartGenerator`**: Uses Plotly's `make_subplots` to create a 4-panel technical analysis dashboard where zooming on the price also zooms the RSI and MACD.
- **`PortfolioVisualizer`**: Implements specialized charts for portfolio management, including a "Sharpe Ratio" bubble chart.
- **Technical Indicators**: Includes manual implementations of RSI and MACD to demonstrate the underlying math.

## How to Run
1. Install dependencies: `pip install pandas numpy matplotlib seaborn plotly yfinance`
2. Run the demonstration:
```bash
python week_05/daythirty/day_thirty.py
```

## Reflection
Data visualization is the bridge between raw numbers and actionable insights. Interactive charts, in particular, allow traders to "feel" the data by exploring different timeframes and indicators dynamically.
