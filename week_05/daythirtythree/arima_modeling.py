"""
ARIMA Modeling for Financial Time Series
Autoregressive Integrated Moving Average models
"""

import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')


class ARIMAModeler:
    """
    ARIMA modeling for financial time series forecasting
    """

    def __init__(self):
        self.models = {}
        self.forecasts = {}

    def find_optimal_arima_order(self, series, max_p=5, max_d=2, max_q=5,
                                 method='aic', seasonal=False):
        """
        Find optimal ARIMA order using information criteria
        """
        best_score = float('inf')
        best_order = (0, 0, 0)

        if seasonal:
            # Seasonal ARIMA
            for p in range(max_p + 1):
                for d in range(max_d + 1):
                    for q in range(max_q + 1):
                        try:
                            if seasonal:
                                model = SARIMAX(series, order=(p, d, q),
                                                seasonal_order=(0, 0, 0, 0))
                            else:
                                model = ARIMA(series, order=(p, d, q))

                            fitted_model = model.fit()

                            if method == 'aic':
                                score = fitted_model.aic
                            elif method == 'bic':
                                score = fitted_model.bic
                            else:
                                score = fitted_model.aic

                            if score < best_score:
                                best_score = score
                                best_order = (p, d, q)

                        except:
                            continue
        else:
            # Regular ARIMA
            for p in range(max_p + 1):
                for d in range(max_d + 1):
                    for q in range(max_q + 1):
                        try:
                            model = ARIMA(series, order=(p, d, q))
                            fitted_model = model.fit()

                            if method == 'aic':
                                score = fitted_model.aic
                            elif method == 'bic':
                                score = fitted_model.bic
                            else:
                                score = fitted_model.aic

                            if score < best_score:
                                best_score = score
                                best_order = (p, d, q)

                        except:
                            continue

        return best_order, best_score

    def fit_arima_model(self, series, order, seasonal_order=None,
                        enforce_stationarity=True, enforce_invertibility=True):
        """
        Fit ARIMA model to time series
        """
        try:
            if seasonal_order:
                model = SARIMAX(series,
                                order=order,
                                seasonal_order=seasonal_order,
                                enforce_stationarity=enforce_stationarity,
                                enforce_invertibility=enforce_invertibility)
            else:
                model = ARIMA(series, order=order)

            fitted_model = model.fit()
            return fitted_model

        except Exception as e:
            print(f"Error fitting ARIMA model: {e}")
            return None

    def forecast_arima(self, model, steps=30, alpha=0.05):
        """
        Generate forecasts from ARIMA model
        """
        try:
            forecast_result = model.get_forecast(steps=steps)
            forecast = forecast_result.predicted_mean
            confidence_intervals = forecast_result.conf_int(alpha=alpha)

            return {
                'forecast': forecast,
                'confidence_intervals': confidence_intervals,
                'forecast_object': forecast_result
            }
        except Exception as e:
            print(f"Error generating forecast: {e}")
            return None

    def rolling_arima_forecast(self, series, order, train_size=0.8,
                               forecast_horizon=10, step=1):
        """
        Perform rolling ARIMA forecasting
        """
        n = len(series)
        train_end = int(n * train_size)

        forecasts = []
        actuals = []
        forecast_dates = []

        for i in range(train_end, n - forecast_horizon + 1, step):
            # Training data
            train_data = series[:i]

            try:
                # Fit model
                model = self.fit_arima_model(train_data, order)
                if model is None:
                    continue

                # Generate forecast
                forecast_result = self.forecast_arima(
                    model, steps=forecast_horizon)
                if forecast_result is None:
                    continue

                # Store results
                # First step forecast
                forecast_value = forecast_result['forecast'].iloc[0]
                actual_value = series.iloc[i]

                forecasts.append(forecast_value)
                actuals.append(actual_value)
                forecast_dates.append(series.index[i])

            except Exception as e:
                print(f"Error in rolling forecast at step {i}: {e}")
                continue

        # Calculate forecast accuracy
        if len(forecasts) > 0:
            mse = mean_squared_error(actuals, forecasts)
            mae = mean_absolute_error(actuals, forecasts)
            rmse = np.sqrt(mse)

            accuracy = {
                'mse': mse,
                'mae': mae,
                'rmse': rmse,
                'forecast_bias': np.mean(np.array(forecasts) - np.array(actuals))
            }
        else:
            accuracy = {}

        return {
            'forecasts': forecasts,
            'actuals': actuals,
            'dates': forecast_dates,
            'accuracy': accuracy
        }

    def plot_arima_results(self, series, model, forecast_result, title="ARIMA Forecast"):
        """Plot ARIMA model results and forecasts"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot historical data
        ax.plot(series.index, series.values, label='Historical', color='blue')

        # Plot forecast
        forecast = forecast_result['forecast']
        conf_int = forecast_result['confidence_intervals']

        ax.plot(forecast.index, forecast.values, label='Forecast', color='red')
        ax.fill_between(conf_int.index,
                        conf_int.iloc[:, 0],
                        conf_int.iloc[:, 1],
                        color='pink', alpha=0.3, label='95% Confidence Interval')

        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def diagnostic_plots(self, model):
        """Generate diagnostic plots for ARIMA model"""
        try:
            # Residuals
            residuals = model.resid

            fig, axes = plt.subplots(2, 2, figsize=(12, 10))

            # Residuals plot
            axes[0, 0].plot(residuals)
            axes[0, 0].set_title('Residuals')
            axes[0, 0].set_xlabel('Time')
            axes[0, 0].set_ylabel('Residuals')
            axes[0, 0].grid(True, alpha=0.3)

            # Q-Q plot
            from scipy import stats
            stats.probplot(residuals.dropna(), dist="norm", plot=axes[0, 1])
            axes[0, 1].set_title('Q-Q Plot')

            # ACF of residuals
            plot_acf(residuals.dropna(), ax=axes[1, 0])
            axes[1, 0].set_title('ACF of Residuals')

            # Histogram of residuals
            axes[1, 1].hist(residuals.dropna(), bins=30,
                            alpha=0.7, edgecolor='black')
            axes[1, 1].set_title('Distribution of Residuals')
            axes[1, 1].set_xlabel('Residuals')
            axes[1, 1].set_ylabel('Frequency')

            plt.tight_layout()
            plt.show()

            # Ljung-Box test for autocorrelation in residuals
            from statsmodels.stats.diagnostic import acorr_ljungbox
            lb_test = acorr_ljungbox(
                residuals.dropna(), lags=10, return_df=True)
            print("Ljung-Box Test for Residual Autocorrelation:")
            print(lb_test)

        except Exception as e:
            print(f"Error generating diagnostic plots: {e}")

    def compare_multiple_models(self, series, orders_list):
        """Compare multiple ARIMA models"""
        comparison_results = []

        for order in orders_list:
            try:
                model = self.fit_arima_model(series, order)
                if model is None:
                    continue

                # Calculate metrics
                aic = model.aic
                bic = model.bic
                mse = np.mean(model.resid ** 2)

                comparison_results.append({
                    'order': order,
                    'aic': aic,
                    'bic': bic,
                    'mse': mse,
                    'model': model
                })

            except Exception as e:
                print(f"Error with order {order}: {e}")
                continue

        # Sort by AIC (lower is better)
        comparison_results.sort(key=lambda x: x['aic'])

        return comparison_results


def demonstrate_arima_modeling():
    """Demonstrate ARIMA modeling capabilities"""
    print("ARIMA Modeling Demonstration")
    print("=" * 50)

    modeler = ARIMAModeler()

    # Load sample data
    symbol = 'AAPL'
    stock = yf.Ticker(symbol)
    data = stock.history(period='3y')
    prices = data['Close']

    # Use returns for stationarity
    returns = prices.pct_change().dropna()

    print(f"Data loaded: {len(prices)} price points, {len(returns)} returns")

    # Find optimal ARIMA order for returns
    print("\n1. Finding optimal ARIMA order...")
    optimal_order, best_score = modeler.find_optimal_arima_order(
        returns, max_p=3, max_d=1, max_q=3, method='aic'
    )
    print(f"Optimal ARIMA order: {optimal_order}")
    print(f"Best AIC: {best_score:.2f}")

    # Fit ARIMA model
    print("\n2. Fitting ARIMA model...")
    model = modeler.fit_arima_model(returns, optimal_order)

    if model is not None:
        print(model.summary())

        # Generate forecast
        print("\n3. Generating forecasts...")
        forecast_result = modeler.forecast_arima(model, steps=30)

        if forecast_result is not None:
            # Convert returns forecast back to prices
            last_price = prices.iloc[-1]
            returns_forecast = forecast_result['forecast']
            price_forecast = last_price * (1 + returns_forecast).cumprod()

            print(f"Last actual price: ${last_price:.2f}")
            print(
                f"30-day forecast range: ${price_forecast.min():.2f} - ${price_forecast.max():.2f}")

            # Plot results (using returns for demonstration)
            modeler.plot_arima_results(
                returns.tail(100),
                model,
                forecast_result,
                title=f"ARIMA({optimal_order[0]},{optimal_order[1]},{optimal_order[2]}) Forecast for {symbol} Returns"
            )

            # Diagnostic plots
            print("\n4. Generating diagnostic plots...")
            modeler.diagnostic_plots(model)

        # Rolling forecast
        print("\n5. Performing rolling forecast...")
        rolling_results = modeler.rolling_arima_forecast(
            returns, optimal_order, train_size=0.7, forecast_horizon=5, step=5
        )

        if rolling_results['accuracy']:
            print("Rolling Forecast Accuracy:")
            for metric, value in rolling_results['accuracy'].items():
                print(f"  {metric.upper()}: {value:.6f}")

    # Compare multiple models
    print("\n6. Comparing multiple ARIMA models...")
    test_orders = [(1, 0, 1), (1, 1, 1), (2, 1, 2), (0, 1, 1)]
    comparison = modeler.compare_multiple_models(returns, test_orders)

    print("\nModel Comparison (sorted by AIC):")
    for result in comparison[:3]:  # Top 3 models
        print(
            f"  ARIMA{result['order']}: AIC={result['aic']:.2f}, BIC={result['bic']:.2f}")

    return modeler, model, returns


if __name__ == "__main__":
    demonstrate_arima_modeling()
