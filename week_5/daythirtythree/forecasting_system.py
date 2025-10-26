"""
Comprehensive Time Series Forecasting System
Advanced forecasting techniques for financial data
"""

from seasonal_analysis import SeasonalAnalyzer
from garch_volatility import GARCHModeler
from arima_modeling import ARIMAModeler
from stationarity_tests import StationarityAnalyzer
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class TimeSeriesForecastingSystem:
    """
    Comprehensive time series forecasting system for financial data
    """

    def __init__(self):
        self.stationarity_analyzer = StationarityAnalyzer()
        self.arima_modeler = ARIMAModeler()
        self.garch_modeler = GARCHModeler()
        self.seasonal_analyzer = SeasonalAnalyzer()
        self.forecast_results = {}

    def load_data(self, symbol, period='3y'):
        """Load and prepare data for forecasting"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)

            # Calculate returns
            data['Returns'] = data['Close'].pct_change()
            data['Log_Returns'] = np.log(data['Close']).diff()

            return data
        except Exception as e:
            print(f"Error loading data for {symbol}: {e}")
            return None

    def comprehensive_forecast(self, symbol, forecast_horizon=30,
                               confidence_level=0.95):
        """Perform comprehensive forecasting using multiple methods"""
        print(f"Comprehensive Forecasting for {symbol}")
        print("=" * 50)

        # Load data
        data = self.load_data(symbol)
        if data is None:
            return None

        prices = data['Close']
        returns = data['Returns'].dropna()

        forecasts = {}

        # 1. Price-based forecasts
        print("\n1. Price-based forecasting...")
        price_forecasts = self._price_based_forecast(prices, forecast_horizon)
        forecasts['price_based'] = price_forecasts

        # 2. ARIMA forecasting
        print("\n2. ARIMA forecasting...")
        arima_forecasts = self._arima_forecast(prices, forecast_horizon)
        forecasts['arima'] = arima_forecasts

        # 3. Returns-based forecasting
        print("\n3. Returns-based forecasting...")
        returns_forecasts = self._returns_based_forecast(
            returns, prices, forecast_horizon)
        forecasts['returns_based'] = returns_forecasts

        # 4. Volatility forecasting
        print("\n4. Volatility forecasting...")
        volatility_forecasts = self._volatility_forecast(
            returns, forecast_horizon)
        forecasts['volatility'] = volatility_forecasts

        # 5. Ensemble forecast
        print("\n5. Ensemble forecasting...")
        ensemble_forecast = self._create_ensemble_forecast(forecasts, prices)
        forecasts['ensemble'] = ensemble_forecast

        # Store results
        self.forecast_results[symbol] = {
            'forecasts': forecasts,
            'actual_data': data,
            'forecast_date': datetime.now(),
            'forecast_horizon': forecast_horizon
        }

        return forecasts

    def _price_based_forecast(self, prices, horizon):
        """Simple price-based forecasting methods"""
        # Moving average forecast
        ma_short = prices.rolling(window=20).mean().iloc[-1]
        ma_long = prices.rolling(window=50).mean().iloc[-1]

        # Exponential smoothing
        from statsmodels.tsa.holtwinters import SimpleExpSmoothing
        try:
            model = SimpleExpSmoothing(prices).fit()
            exp_smooth_forecast = model.forecast(horizon)
        except:
            exp_smooth_forecast = pd.Series([prices.iloc[-1]] * horizon)

        # Random walk forecast (no change)
        random_walk_forecast = pd.Series([prices.iloc[-1]] * horizon)

        return {
            'moving_average_short': ma_short,
            'moving_average_long': ma_long,
            'exponential_smoothing': exp_smooth_forecast,
            'random_walk': random_walk_forecast
        }

    def _arima_forecast(self, prices, horizon):
        """ARIMA-based forecasting"""
        # Use returns for stationarity
        returns = prices.pct_change().dropna()

        # Find optimal ARIMA order
        optimal_order, _ = self.arima_modeler.find_optimal_arima_order(
            returns, max_p=3, max_d=1, max_q=3
        )

        # Fit ARIMA model
        model = self.arima_modeler.fit_arima_model(returns, optimal_order)

        if model is None:
            return None

        # Generate returns forecast
        returns_forecast = self.arima_modeler.forecast_arima(
            model, steps=horizon)

        if returns_forecast is None:
            return None

        # Convert returns forecast to price forecast
        last_price = prices.iloc[-1]
        cumulative_returns = (1 + returns_forecast['forecast']).cumprod()
        price_forecast = last_price * cumulative_returns

        return {
            'model': model,
            'returns_forecast': returns_forecast,
            'price_forecast': price_forecast,
            'order': optimal_order
        }

    def _returns_based_forecast(self, returns, prices, horizon):
        """Returns-based forecasting methods"""
        # Historical mean returns
        mean_return = returns.mean()
        last_price = prices.iloc[-1]

        # Simple projection
        simple_projection = last_price * \
            (1 + mean_return) ** np.arange(1, horizon + 1)

        # Monte Carlo simulation
        mc_forecasts = self._monte_carlo_forecast(
            returns, last_price, horizon, n_simulations=1000)

        return {
            'mean_returns_projection': simple_projection,
            'monte_carlo': mc_forecasts
        }

    def _monte_carlo_forecast(self, returns, last_price, horizon, n_simulations=1000):
        """Monte Carlo simulation for price forecasting"""
        mu = returns.mean()
        sigma = returns.std()

        simulations = np.zeros((n_simulations, horizon))

        for i in range(n_simulations):
            # Generate random returns
            random_returns = np.random.normal(mu, sigma, horizon)
            # Calculate price path
            price_path = last_price * (1 + random_returns).cumprod()
            simulations[i] = price_path

        # Calculate statistics
        mean_forecast = simulations.mean(axis=0)
        median_forecast = np.median(simulations, axis=0)
        confidence_95_lower = np.percentile(simulations, 2.5, axis=0)
        confidence_95_upper = np.percentile(simulations, 97.5, axis=0)

        return {
            'mean': mean_forecast,
            'median': median_forecast,
            'confidence_95_lower': confidence_95_lower,
            'confidence_95_upper': confidence_95_upper,
            'all_simulations': simulations
        }

    def _volatility_forecast(self, returns, horizon):
        """Volatility forecasting using GARCH"""
        # Fit GARCH model
        garch_model = self.garch_modeler.fit_garch_model(returns, p=1, q=1)

        if garch_model is None:
            return None

        # Generate volatility forecast
        volatility_forecast = self.garch_modeler.forecast_volatility(
            garch_model, horizon)

        # Calculate Value at Risk
        var_95 = self.garch_modeler.value_at_risk_garch(
            garch_model, returns, 0.05)
        var_99 = self.garch_modeler.value_at_risk_garch(
            garch_model, returns, 0.01)

        return {
            'garch_model': garch_model,
            'volatility_forecast': volatility_forecast,
            'current_var_95': var_95.iloc[-1],
            'current_var_99': var_99.iloc[-1]
        }

    def _create_ensemble_forecast(self, individual_forecasts, actual_prices):
        """Create ensemble forecast from multiple methods"""
        # Extract point forecasts from different methods
        point_forecasts = []

        # From ARIMA
        if individual_forecasts.get('arima') and individual_forecasts['arima'].get('price_forecast'):
            arima_forecast = individual_forecasts['arima']['price_forecast']
            point_forecasts.append(arima_forecast)

        # From returns-based (Monte Carlo mean)
        if individual_forecasts.get('returns_based'):
            mc_mean = individual_forecasts['returns_based']['monte_carlo']['mean']
            point_forecasts.append(pd.Series(mc_mean))

        # Simple average ensemble
        if point_forecasts:
            # Align all forecasts
            min_length = min(len(f) for f in point_forecasts)
            aligned_forecasts = [f.iloc[:min_length] if hasattr(f, 'iloc') else pd.Series(f[:min_length])
                                 for f in point_forecasts]

            # Calculate ensemble
            ensemble_array = np.array([f.values for f in aligned_forecasts])
            ensemble_mean = np.mean(ensemble_array, axis=0)
            ensemble_std = np.std(ensemble_array, axis=0)

            ensemble_forecast = pd.Series(ensemble_mean)
            confidence_lower = ensemble_forecast - 1.96 * ensemble_std
            confidence_upper = ensemble_forecast + 1.96 * ensemble_std

        else:
            # Fallback to last price
            ensemble_forecast = pd.Series([actual_prices.iloc[-1]] * 30)
            confidence_lower = ensemble_forecast * 0.9
            confidence_upper = ensemble_forecast * 1.1

        return {
            'point_forecast': ensemble_forecast,
            'confidence_lower': confidence_lower,
            'confidence_upper': confidence_upper
        }

    def plot_forecast_comparison(self, symbol, forecast_horizon=30):
        """Plot comparison of all forecasting methods"""
        if symbol not in self.forecast_results:
            print(f"No forecast results for {symbol}")
            return

        forecasts = self.forecast_results[symbol]['forecasts']
        actual_data = self.forecast_results[symbol]['actual_data']

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()

        # Plot 1: Price forecasts
        ax = axes[0]
        actual_data['Close'].tail(100).plot(ax=ax, label='Actual', linewidth=2)

        # Plot different forecasts
        forecast_dates = pd.date_range(
            start=actual_data.index[-1], periods=forecast_horizon+1, freq='D')[1:]

        if forecasts.get('arima') and forecasts['arima'].get('price_forecast'):
            forecasts['arima']['price_forecast'].plot(
                ax=ax, label='ARIMA', linestyle='--')

        if forecasts.get('returns_based'):
            mc_mean = forecasts['returns_based']['monte_carlo']['mean']
            ax.plot(forecast_dates[:len(mc_mean)], mc_mean,
                    label='Monte Carlo', linestyle='--')

        if forecasts.get('ensemble'):
            ensemble = forecasts['ensemble']['point_forecast']
            ax.plot(forecast_dates[:len(ensemble)], ensemble,
                    label='Ensemble', linestyle='--', linewidth=2)

            # Plot confidence interval
            lower = forecasts['ensemble']['confidence_lower']
            upper = forecasts['ensemble']['confidence_upper']
            ax.fill_between(
                forecast_dates[:len(ensemble)], lower, upper, alpha=0.2, label='95% CI')

        ax.set_title(f'Price Forecast Comparison - {symbol}')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Plot 2: Volatility forecast
        ax = axes[1]
        if forecasts.get('volatility'):
            vol_forecast = forecasts['volatility']['volatility_forecast']['volatility_annualized']
            ax.plot(range(1, len(vol_forecast) + 1), vol_forecast, marker='o')
            ax.set_title('Volatility Forecast (Annualized)')
            ax.set_xlabel('Days Ahead')
            ax.set_ylabel('Volatility')
            ax.grid(True, alpha=0.3)

        # Plot 3: Monte Carlo simulations
        ax = axes[2]
        if forecasts.get('returns_based'):
            simulations = forecasts['returns_based']['monte_carlo']['all_simulations']
            # Plot a subset of simulations
            for i in range(min(50, simulations.shape[0])):
                ax.plot(forecast_dates,
                        simulations[i], alpha=0.1, color='blue')

            # Plot mean and confidence intervals
            ax.plot(forecast_dates, forecasts['returns_based']['monte_carlo']['mean'],
                    color='red', linewidth=2, label='Mean')
            ax.plot(forecast_dates, forecasts['returns_based']['monte_carlo']['confidence_95_lower'],
                    color='red', linestyle='--', alpha=0.7, label='95% CI')
            ax.plot(forecast_dates, forecasts['returns_based']['monte_carlo']['confidence_95_upper'],
                    color='red', linestyle='--', alpha=0.7)

            ax.set_title('Monte Carlo Simulations')
            ax.legend()
            ax.grid(True, alpha=0.3)

        # Plot 4: Forecast error analysis (if we had historical forecasts)
        ax = axes[3]
        # This would typically show historical forecast accuracy
        ax.text(0.5, 0.5, 'Forecast Error Analysis\n(Historical Performance)',
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Forecast Accuracy')
        ax.axis('off')

        plt.tight_layout()
        plt.show()

    def backtest_forecasts(self, symbol, forecast_horizon=30, test_size=0.2):
        """Backtest forecasting methods on historical data"""
        data = self.load_data(symbol)
        if data is None:
            return None

        prices = data['Close']
        n_test = int(len(prices) * test_size)

        # Use Time Series Split for backtesting
        tscv = TimeSeriesSplit(n_splits=5)

        backtest_results = {
            'arima_errors': [],
            'monte_carlo_errors': [],
            'ensemble_errors': []
        }

        for train_idx, test_idx in tscv.split(prices):
            train_data = prices.iloc[train_idx]
            test_data = prices.iloc[test_idx]

            # Ensure we have enough test data
            if len(test_data) < forecast_horizon:
                continue

            # Test ARIMA
            try:
                arima_forecast = self._arima_forecast(
                    train_data, forecast_horizon)
                if arima_forecast and arima_forecast.get('price_forecast'):
                    # First step forecast
                    arima_pred = arima_forecast['price_forecast'].iloc[0]
                    arima_actual = test_data.iloc[0]
                    arima_error = (arima_pred - arima_actual) / arima_actual
                    backtest_results['arima_errors'].append(arima_error)
            except:
                pass

            # Test Monte Carlo
            try:
                returns = train_data.pct_change().dropna()
                mc_forecast = self._monte_carlo_forecast(
                    returns, train_data.iloc[-1], 1)
                mc_pred = mc_forecast['mean'][0]
                mc_actual = test_data.iloc[0]
                mc_error = (mc_pred - mc_actual) / mc_actual
                backtest_results['monte_carlo_errors'].append(mc_error)
            except:
                pass

        # Calculate performance metrics
        performance = {}
        for method, errors in backtest_results.items():
            if errors:
                performance[method] = {
                    'mean_absolute_error': np.mean(np.abs(errors)),
                    'root_mean_squared_error': np.sqrt(np.mean(np.array(errors) ** 2)),
                    'mean_error': np.mean(errors)
                }

        return performance


def demonstrate_forecasting_system():
    """Demonstrate the comprehensive forecasting system"""
    print("Time Series Forecasting System Demonstration")
    print("=" * 50)

    forecasting_system = TimeSeriesForecastingSystem()

    # Symbol to analyze
    symbol = 'AAPL'

    # Perform comprehensive forecast
    print(f"Running comprehensive forecast for {symbol}...")
    forecasts = forecasting_system.comprehensive_forecast(
        symbol, forecast_horizon=30)

    if forecasts is None:
        print("Forecasting failed")
        return

    # Print forecast summary
    print("\nFORECAST SUMMARY")
    print("=" * 30)

    # Ensemble forecast
    if forecasts.get('ensemble'):
        ensemble = forecasts['ensemble']['point_forecast']
        print(f"Ensemble Forecast:")
        print(f"  1-day: ${ensemble.iloc[0]:.2f}")
        print(f"  7-day: ${ensemble.iloc[6]:.2f}")
        print(f"  30-day: ${ensemble.iloc[-1]:.2f}")

    # Volatility forecast
    if forecasts.get('volatility'):
        vol_forecast = forecasts['volatility']['volatility_forecast']['volatility_annualized']
        print(f"\nVolatility Forecast:")
        print(f"  Current: {vol_forecast[0]:.2%}")
        print(f"  30-day: {vol_forecast[-1]:.2%}")

    # Value at Risk
    if forecasts.get('volatility'):
        var_95 = forecasts['volatility']['current_var_95']
        var_99 = forecasts['volatility']['current_var_99']
        print(f"\nValue at Risk (1-day):")
        print(f"  95% Confidence: {var_95:.2%}")
        print(f"  99% Confidence: {var_99:.2%}")

    # Plot forecast comparison
    print("\nGenerating forecast plots...")
    forecasting_system.plot_forecast_comparison(symbol)

    # Backtest forecasts
    print("\nRunning backtest...")
    backtest_results = forecasting_system.backtest_forecasts(symbol)

    if backtest_results:
        print("\nBACKTEST RESULTS")
        print("=" * 30)
        for method, metrics in backtest_results.items():
            print(f"\n{method.replace('_', ' ').title()}:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value:.4f}")

    return forecasting_system, forecasts


if __name__ == "__main__":
    demonstrate_forecasting_system()
