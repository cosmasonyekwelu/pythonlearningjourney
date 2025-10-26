"""
Day 33 — Time Series Analysis
-----------------------------
Advanced time series analysis techniques for financial data.
Integrated with Day 33 modules for comprehensive analysis.
"""

from forecasting_system import TimeSeriesForecastingSystem
from seasonal_analysis import SeasonalAnalyzer
from garch_volatility import GARCHModeler
from arima_modeling import ARIMAModeler
from stationarity_tests import StationarityAnalyzer
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import warnings
import sys
import os

# Add the current directory to path to import Day 33 modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Day 33 modules

# ==============================
# Configuration
# ==============================
TRADING_DAYS = 252
RISK_FREE_RATE = 0.02
plt.style.use("seaborn-v0_8-darkgrid")
warnings.filterwarnings('ignore')


class FinancialTimeSeries:
    """
    Financial time series analysis class for a given symbol.
    Integrates all Day 33 modules for comprehensive analysis.
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

        # Calculate derived series
        self.returns = self.data["Close"].pct_change().dropna()
        self.log_returns = np.log(self.data["Close"]).diff().dropna()

        # Initialize Day 33 analyzers
        self.stationarity_analyzer = StationarityAnalyzer()
        self.arima_modeler = ARIMAModeler()
        self.garch_modeler = GARCHModeler()
        self.seasonal_analyzer = SeasonalAnalyzer()
        self.forecasting_system = TimeSeriesForecastingSystem()

        print(
            f"Data successfully loaded for {self.symbol} ({len(self.data)} rows).")

    # ==========================
    # Comprehensive Stationarity Testing
    # ==========================
    def test_stationarity(self, timeseries: pd.Series = None) -> dict:
        """
        Perform comprehensive stationarity testing using Day 33 module.
        """
        if timeseries is None:
            timeseries = self.returns

        print("\n" + "="*50)
        print("COMPREHENSIVE STATIONARITY ANALYSIS")
        print("="*50)

        # Use Day 33 stationarity analyzer
        result = self.stationarity_analyzer.comprehensive_stationarity_test(
            timeseries)

        print(f"\nADF Test:")
        print(f"  p-value: {result['adf_test']['p_value']:.4f}")
        print(f"  Stationary: {result['adf_test']['stationary']}")

        print(f"\nKPSS Test:")
        print(f"  p-value: {result['kpss_test']['p_value']:.4f}")
        print(f"  Stationary: {result['kpss_test']['stationary']}")

        print(f"\nConclusion: {result['conclusion']}")

        # Plot ACF/PACF
        print("\nGenerating ACF/PACF plots...")
        self.stationarity_analyzer.plot_autocorrelation(timeseries, lags=40)

        return result

    # ==========================
    # Advanced Seasonal Decomposition
    # ==========================
    def decompose_series(self, series: pd.Series = None, model: str = "additive", period: int = 252):
        """
        Perform advanced seasonal decomposition using Day 33 module.
        """
        if series is None:
            series = self.data["Close"]

        print("\n" + "="*50)
        print("SEASONAL DECOMPOSITION ANALYSIS")
        print("="*50)

        # Use Day 33 seasonal analyzer
        decomposition = self.seasonal_analyzer.seasonal_decomposition(
            series, model=model, period=period
        )

        if decomposition is not None:
            self.seasonal_analyzer.plot_decomposition(
                decomposition,
                title=f"Seasonal Decomposition - {self.symbol}"
            )

        # Analyze seasonal patterns
        print("\nAnalyzing seasonal patterns...")
        patterns = self.seasonal_analyzer.analyze_seasonal_patterns(
            series, frequency='D')
        if patterns:
            self.seasonal_analyzer.plot_seasonal_patterns(
                patterns,
                title=f"Seasonal Patterns - {self.symbol}"
            )

        return decomposition, patterns

    # ==========================
    # Advanced ARIMA Modeling
    # ==========================
    def fit_arima(self, series: pd.Series = None, order=None, forecast_steps=30):
        """
        Fit ARIMA model with automatic order selection using Day 33 module.
        """
        if series is None:
            series = self.data["Close"]

        print("\n" + "="*50)
        print("ARIMA MODELING & FORECASTING")
        print("="*50)

        # Find optimal ARIMA order if not specified
        if order is None:
            print("Finding optimal ARIMA order...")
            optimal_order, best_score = self.arima_modeler.find_optimal_arima_order(
                series, max_p=3, max_d=2, max_q=3
            )
            order = optimal_order
            print(f"Optimal ARIMA order: {order} (AIC: {best_score:.2f})")
        else:
            print(f"Using specified ARIMA order: {order}")

        # Fit ARIMA model
        fitted_model = self.arima_modeler.fit_arima_model(series, order)

        if fitted_model is None:
            print("ARIMA model fitting failed.")
            return None, None

        print(fitted_model.summary())

        # Generate forecast
        forecast_result = self.arima_modeler.forecast_arima(
            fitted_model, steps=forecast_steps)

        if forecast_result is not None:
            print(f"\nARIMA{order} Forecast (Next {forecast_steps} days):")
            for i, (date, value) in enumerate(zip(forecast_result['forecast'].index,
                                                  forecast_result['forecast'].values)):
                print(f"  Day {i+1}: {value:.2f}")

            # Plot results
            self.arima_modeler.plot_arima_results(
                series.tail(100),
                fitted_model,
                forecast_result,
                title=f"ARIMA{order} Forecast - {self.symbol}"
            )

            # Diagnostic plots
            print("\nGenerating diagnostic plots...")
            self.arima_modeler.diagnostic_plots(fitted_model)

        return fitted_model, forecast_result

    # ==========================
    # Advanced GARCH Volatility Modeling
    # ==========================
    def forecast_volatility(self, p=1, q=1, forecast_horizon=10):
        """
        Fit GARCH model and forecast volatility using Day 33 module.
        """
        print("\n" + "="*50)
        print("GARCH VOLATILITY MODELING")
        print("="*50)

        # Test for volatility clustering
        print("Testing for volatility clustering...")
        clustering_test = self.garch_modeler.volatility_clustering_test(
            self.returns)

        # Test for leverage effect
        print("Testing for leverage effect...")
        leverage_test = self.garch_modeler.leverage_effect_test(self.returns)

        # Fit multiple GARCH models and select best
        print("Fitting multiple GARCH models...")
        orders_to_test = [(1, 1), (1, 2), (2, 1), (2, 2)]
        comparison = self.garch_modeler.fit_multiple_garch_models(
            self.returns, orders_to_test)

        if comparison:
            best_model = comparison[0]['model']
            best_order = comparison[0]['order']
            print(
                f"Best model: GARCH{best_order} (AIC: {comparison[0]['aic']:.2f})")

            # Generate volatility forecast
            forecast_result = self.garch_modeler.forecast_volatility(
                best_model, horizon=forecast_horizon
            )

            if forecast_result is not None:
                print(
                    f"\nVolatility Forecast (Annualized, Next {forecast_horizon} days):")
                for i, vol in enumerate(forecast_result['volatility_annualized']):
                    print(f"  Day {i+1}: {vol:.2%}")

            # Calculate historical volatility for comparison
            historical_vol = self.garch_modeler.calculate_historical_volatility(
                self.returns, window=21
            )

            # Plot volatility comparison
            self.garch_modeler.plot_volatility_comparison(
                self.returns, best_model, historical_vol, forecast_result,
                title=f"GARCH{best_order} Volatility - {self.symbol}"
            )

            # Calculate Value at Risk
            var_95 = self.garch_modeler.value_at_risk_garch(
                best_model, self.returns, 0.05)
            var_99 = self.garch_modeler.value_at_risk_garch(
                best_model, self.returns, 0.01)
            print(f"\nValue at Risk (1-day):")
            print(f"  95% Confidence: {var_95.iloc[-1]:.2%}")
            print(f"  99% Confidence: {var_99.iloc[-1]:.2%}")

            return best_model, forecast_result

        return None, None

    # ==========================
    # Rolling Metrics with Enhanced Analysis
    # ==========================
    def calculate_rolling_metrics(self, window: int = 20):
        """
        Calculate enhanced rolling metrics using multiple approaches.
        """
        print("\n" + "="*50)
        print("ROLLING METRICS ANALYSIS")
        print("="*50)

        # Basic rolling metrics
        rolling_vol = self.returns.rolling(
            window=window).std() * np.sqrt(TRADING_DAYS)
        rolling_sharpe = (
            (self.returns.rolling(window=window).mean()
             * TRADING_DAYS - RISK_FREE_RATE)
            / (rolling_vol + 1e-9)
        )

        # GARCH rolling volatility forecast
        print("Performing rolling volatility forecast...")
        garch_rolling = self.garch_modeler.rolling_volatility_forecast(
            self.returns, p=1, q=1, train_size=0.7, forecast_horizon=5, step=5
        )

        # Plot comparison
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Rolling volatility comparison
        ax1.plot(
            rolling_vol, label=f"{window}-Day Historical Vol", color="orange", alpha=0.7)
        if garch_rolling['forecasts']:
            ax1.scatter(garch_rolling['dates'], garch_rolling['forecasts'],
                        label="GARCH Forecast", color="red", alpha=0.6)
        ax1.set_ylabel("Volatility", color="orange")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_title(f"Rolling Volatility Comparison - {self.symbol}")

        # Rolling Sharpe ratio
        ax2.plot(rolling_sharpe, label="Rolling Sharpe Ratio", color="blue")
        ax2.set_ylabel("Sharpe Ratio", color="blue")
        ax2.axhline(y=0, color='red', linestyle='--',
                    alpha=0.5, label='Zero Line')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        return {
            "rolling_volatility": rolling_vol,
            "rolling_sharpe": rolling_sharpe,
            "garch_rolling": garch_rolling
        }

    # ==========================
    # Comprehensive Forecasting System
    # ==========================
    def comprehensive_forecast(self, forecast_horizon: int = 30):
        """
        Run comprehensive forecasting using Day 33 forecasting system.
        """
        print("\n" + "="*50)
        print("COMPREHENSIVE FORECASTING SYSTEM")
        print("="*50)

        forecasts = self.forecasting_system.comprehensive_forecast(
            self.symbol, forecast_horizon=forecast_horizon
        )

        if forecasts is not None:
            # Display forecast summary
            print("\nFORECAST SUMMARY:")
            print("-" * 30)

            if forecasts.get('ensemble'):
                ensemble = forecasts['ensemble']['point_forecast']
                print(f"Ensemble Forecast:")
                print(f"  1-day: ${ensemble.iloc[0]:.2f}")
                print(f"  7-day: ${ensemble.iloc[6]:.2f}")
                print(f"  {forecast_horizon}-day: ${ensemble.iloc[-1]:.2f}")

            if forecasts.get('volatility'):
                vol_forecast = forecasts['volatility']['volatility_forecast']['volatility_annualized']
                print(f"\nVolatility Forecast:")
                print(f"  Current: {vol_forecast[0]:.2%}")
                print(f"  {forecast_horizon}-day: {vol_forecast[-1]:.2%}")

            # Plot forecast comparison
            self.forecasting_system.plot_forecast_comparison(
                self.symbol, forecast_horizon)

            # Backtest forecasts
            print("\nRunning backtest...")
            backtest_results = self.forecasting_system.backtest_forecasts(
                self.symbol)

            if backtest_results:
                print("\nBACKTEST RESULTS:")
                print("-" * 20)
                for method, metrics in backtest_results.items():
                    print(f"\n{method.replace('_', ' ').title()}:")
                    for metric, value in metrics.items():
                        print(f"  {metric}: {value:.4f}")

        return forecasts

    # ==========================
    # Complete Analysis Summary
    # ==========================
    def run_complete_analysis(self, forecast_horizon: int = 30):
        """
        Run complete time series analysis using all Day 33 modules.
        """
        print("\n" + "="*60)
        print(f"COMPLETE TIME SERIES ANALYSIS - {self.symbol}")
        print("="*60)

        results = {}

        # 1. Stationarity Analysis
        results['stationarity'] = self.test_stationarity()

        # 2. Seasonal Analysis
        results['decomposition'] = self.decompose_series()

        # 3. ARIMA Modeling
        results['arima'] = self.fit_arima(forecast_steps=forecast_horizon)

        # 4. GARCH Volatility
        results['garch'] = self.forecast_volatility(forecast_horizon=10)

        # 5. Rolling Metrics
        results['rolling_metrics'] = self.calculate_rolling_metrics()

        # 6. Comprehensive Forecasting
        results['comprehensive_forecast'] = self.comprehensive_forecast(
            forecast_horizon)

        # 7. Summary Statistics
        results['summary'] = self.summary_statistics()

        print("\n" + "="*60)
        print("ANALYSIS COMPLETED SUCCESSFULLY!")
        print("="*60)

        return results

    # ==========================
    # Summary Statistics
    # ==========================
    def summary_statistics(self):
        """
        Display comprehensive summary statistics.
        """
        stats = {
            "Mean Return": self.returns.mean(),
            "Std Dev of Return": self.returns.std(),
            "Skewness": self.returns.skew(),
            "Kurtosis": self.returns.kurtosis(),
            "Annualized Volatility": self.returns.std() * np.sqrt(TRADING_DAYS),
            "Sharpe Ratio": (self.returns.mean() * TRADING_DAYS - RISK_FREE_RATE)
            / (self.returns.std() * np.sqrt(TRADING_DAYS)),
            "Max Return": self.returns.max(),
            "Min Return": self.returns.min(),
            "VaR (95%)": self.returns.quantile(0.05),
        }

        print("\n" + "="*50)
        print("SUMMARY STATISTICS")
        print("="*50)

        for k, v in stats.items():
            if isinstance(v, float):
                print(f"{k:25}: {v:10.6f}")
            else:
                print(f"{k:25}: {v:10}")

        return pd.DataFrame(stats, index=[self.symbol])


# ==============================
# Main Script Execution
# ==============================
if __name__ == "__main__":
    print("\nDay 33 — Time Series Analysis")
    print("=============================================")
    print("Integrated with Day 33 modules for comprehensive analysis")
    print("=============================================")

    try:
        # Initialize Analyzer
        ts = FinancialTimeSeries("AAPL", period="2y")

        # Run complete analysis
        results = ts.run_complete_analysis(forecast_horizon=30)

        print(f"\nAnalysis completed for {ts.symbol}!")
        print("All results have been saved in the 'results' variable.")

    except Exception as e:
        print(f"Error during analysis: {e}")
        print("Make sure all Day 33 module files are in the same directory:")
        print("  - stationarity_tests.py")
        print("  - arima_modeling.py")
        print("  - garch_volatility.py")
        print("  - seasonal_analysis.py")
        print("  - forecasting_system.py")
