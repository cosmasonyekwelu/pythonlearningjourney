"""
Day 33 — Time Series Analysis
-----------------------------
Advanced time series analysis techniques for financial data.

This script provides:
1. Stationarity testing (ADF)
2. Seasonal decomposition
3. ARIMA forecasting
4. GARCH volatility modeling
5. Rolling metrics (Volatility, Sharpe ratio)
"""

import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
from arch import arch_model
import warnings


# ==============================
# Configuration
# ==============================
TRADING_DAYS = 252
RISK_FREE_RATE = 0.02
plt.style.use("seaborn-v0_8-darkgrid")


class FinancialTimeSeries:
    """
    Financial time series analysis class for a given symbol.
    """

    def __init__(self, symbol: str, period: str = "2y"):
        """
        Initialize the analyzer by downloading data.

        Args:
            symbol (str): Stock ticker symbol.
            period (str): Time period for data (e.g. '1y', '2y', '5y').
        """
        self.symbol = symbol.upper()
        print(f"Downloading historical data for {self.symbol} ({period})...")
        self.data = yf.download(symbol, period=period, progress=False)
        if self.data.empty:
            raise ValueError(f"No data found for {symbol}")
        self.returns = self.data["Close"].pct_change().dropna()
        print(
            f"Data successfully loaded for {self.symbol} ({len(self.data)} rows).")

    # ==========================
    # Stationarity Testing
    # ==========================
    def test_stationarity(self, timeseries: pd.Series = None) -> bool:
        """
        Perform Augmented Dickey-Fuller test for stationarity.
        Returns True if stationary.
        """
        if timeseries is None:
            timeseries = self.returns

        print("\nPerforming Augmented Dickey-Fuller Test:")
        result = adfuller(timeseries.dropna())
        print(f"ADF Statistic: {result[0]:.4f}")
        print(f"p-value: {result[1]:.4f}")
        for key, value in result[4].items():
            print(f"Critical Value {key}: {value:.4f}")

        stationary = result[1] < 0.05
        print(f"Stationary: {stationary}")
        return stationary

    # ==========================
    # Seasonal Decomposition
    # ==========================
    def decompose_series(self, series: pd.Series = None, model: str = "additive", period: int = 252):
        """
        Perform seasonal decomposition of a time series.

        Args:
            series: The series to decompose (default: closing prices)
            model: 'additive' or 'multiplicative'
            period: Seasonal period (default 252 trading days)
        """
        if series is None:
            series = self.data["Close"]

        print("\nPerforming seasonal decomposition...")
        decomposition = seasonal_decompose(series, model=model, period=period)

        fig, axes = plt.subplots(4, 1, figsize=(12, 10))
        decomposition.observed.plot(ax=axes[0], title="Observed")
        decomposition.trend.plot(ax=axes[1], title="Trend")
        decomposition.seasonal.plot(ax=axes[2], title="Seasonal")
        decomposition.resid.plot(ax=axes[3], title="Residuals")
        plt.tight_layout()
        plt.show()

        return decomposition

    # ==========================
    # ARIMA Forecasting
    # ==========================
    def fit_arima(self, series: pd.Series = None, order=(2, 1, 2), forecast_steps=5):
        """
        Fit ARIMA model to time series and forecast future prices.

        Args:
            series: Series to model (default: closing prices)
            order: ARIMA order (p, d, q)
            forecast_steps: Forecast horizon in days
        """
        if series is None:
            series = self.data["Close"]

        print(f"\nFitting ARIMA{order} model...")
        model = ARIMA(series, order=order)
        fitted_model = model.fit()
        print(fitted_model.summary())

        forecast = fitted_model.forecast(steps=forecast_steps)
        print("\nNext 5-Day Forecast:")
        print(forecast)

        plt.figure(figsize=(10, 5))
        plt.plot(series[-100:], label="Historical Data")
        plt.plot(range(len(series), len(series) + forecast_steps),
                 forecast, label="Forecast", linestyle="--")
        plt.title(f"ARIMA{order} Forecast - {self.symbol}")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

        return fitted_model, forecast

    # ==========================
    # GARCH Volatility Modeling
    # ==========================
    def forecast_volatility(self, p=1, q=1):
        """
        Fit GARCH model to returns and forecast volatility.
        """
        print("\nFitting GARCH model for volatility forecasting...")
        model = arch_model(self.returns * 100, vol="Garch", p=p, q=q)
        fitted_model = model.fit(disp="off")
        forecast = fitted_model.forecast(horizon=5)
        forecast_vol = np.sqrt(forecast.variance.values[-1, :])
        print("Forecast Volatility (Next 5 Days):")
        print(forecast_vol)

        plt.figure(figsize=(10, 4))
        plt.plot(fitted_model.conditional_volatility,
                 label="Conditional Volatility")
        plt.title(f"GARCH({p}, {q}) Volatility - {self.symbol}")
        plt.xlabel("Date")
        plt.ylabel("Volatility (%)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.show()

        return fitted_model, forecast_vol

    # ==========================
    # Rolling Metrics
    # ==========================
    def calculate_rolling_metrics(self, window: int = 20):
        """
        Calculate rolling volatility and Sharpe ratio.

        Args:
            window: Rolling window size in days.
        """
        print("\nCalculating rolling volatility and Sharpe ratio...")
        rolling_vol = self.returns.rolling(
            window=window).std() * np.sqrt(TRADING_DAYS)
        rolling_sharpe = (
            (self.returns.rolling(window=window).mean()
             * TRADING_DAYS - RISK_FREE_RATE)
            / (rolling_vol + 1e-9)
        )

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(rolling_vol, label="Rolling Volatility", color="orange")
        ax1.set_ylabel("Volatility", color="orange")
        ax2 = ax1.twinx()
        ax2.plot(rolling_sharpe, label="Rolling Sharpe Ratio", color="blue")
        ax2.set_ylabel("Sharpe Ratio", color="blue")
        plt.title(f"Rolling Metrics ({window}-Day Window) - {self.symbol}")
        plt.show()

        return pd.DataFrame({
            "Rolling Volatility": rolling_vol,
            "Rolling Sharpe Ratio": rolling_sharpe
        })

    # ==========================
    # Summary Statistics
    # ==========================
    def summary_statistics(self):
        """
        Display summary statistics for price and return series.
        """
        stats = {
            "Mean Return": self.returns.mean(),
            "Std Dev of Return": self.returns.std(),
            "Skewness": self.returns.skew(),
            "Kurtosis": self.returns.kurtosis(),
            "Annualized Volatility": self.returns.std() * np.sqrt(TRADING_DAYS),
            "Sharpe Ratio": (self.returns.mean() * TRADING_DAYS - RISK_FREE_RATE)
            / (self.returns.std() * np.sqrt(TRADING_DAYS)),
        }
        print("\nSummary Statistics:")
        for k, v in stats.items():
            print(f"{k:25}: {v:10.6f}")

        return pd.DataFrame(stats, index=[self.symbol])


# ==============================
# Main Script Execution
# ==============================
if __name__ == "__main__":
    print("\nDay 33 — Time Series Analysis")
    print("=============================================")

    # Initialize Analyzer
    ts = FinancialTimeSeries("AAPL", period="2y")

    # 1. Stationarity Test
    ts.test_stationarity(ts.returns)

    # 2. Decomposition
    ts.decompose_series(ts.data["Close"])

    # 3. ARIMA Forecast
    ts.fit_arima(ts.data["Close"], order=(2, 1, 2), forecast_steps=5)

    # 4. GARCH Volatility
    ts.forecast_volatility(p=1, q=1)

    # 5. Rolling Metrics
    ts.calculate_rolling_metrics(window=20)

    # 6. Summary Statistics
    ts.summary_statistics()

    print("\nTime Series Analysis completed successfully.")
