"""
GARCH Models for Volatility Forecasting
Generalized Autoregressive Conditional Heteroskedasticity models
"""

import pandas as pd
import numpy as np
import yfinance as yf
from arch import arch_model
from arch.univariate import GARCH, ARCH, HARX, ConstantMean, ZeroMean, ARX
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class GARCHModeler:
    """
    GARCH modeling for financial volatility forecasting
    """
    
    def __init__(self):
        self.models = {}
        self.forecasts = {}
    
    def fit_garch_model(self, returns, p=1, q=1, mean='constant', 
                       vol='GARCH', dist='normal'):
        """
        Fit GARCH model to returns data
        """
        try:
            # Scale returns for numerical stability
            scaled_returns = returns * 100
            
            # Create model specification
            if mean == 'constant':
                mean_model = ConstantMean(scaled_returns)
            elif mean == 'zero':
                mean_model = ZeroMean(scaled_returns)
            elif mean == 'ar':
                mean_model = ARX(scaled_returns, lags=1)
            else:
                mean_model = ConstantMean(scaled_returns)
            
            # Create volatility specification
            if vol == 'GARCH':
                vol_model = GARCH(p=p, q=q)
            elif vol == 'ARCH':
                vol_model = ARCH(p=p)
            else:
                vol_model = GARCH(p=p, q=q)
            
            # Create and fit model
            model = arch_model(scaled_returns, mean=mean_model, vol=vol_model, dist=dist)
            fitted_model = model.fit(disp='off')
            
            return fitted_model
            
        except Exception as e:
            print(f"Error fitting GARCH model: {e}")
            return None
    
    def fit_multiple_garch_models(self, returns, orders_list):
        """Fit multiple GARCH models and compare"""
        comparison_results = []
        
        for p, q in orders_list:
            try:
                model = self.fit_garch_model(returns, p=p, q=q)
                if model is not None:
                    comparison_results.append({
                        'order': (p, q),
                        'aic': model.aic,
                        'bic': model.bic,
                        'log_likelihood': model.loglikelihood,
                        'model': model
                    })
            except Exception as e:
                print(f"Error with GARCH({p},{q}): {e}")
                continue
        
        # Sort by AIC
        comparison_results.sort(key=lambda x: x['aic'])
        return comparison_results
    
    def forecast_volatility(self, model, horizon=5):
        """Generate volatility forecasts"""
        try:
            forecast = model.forecast(horizon=horizon, reindex=False)
            
            # Extract volatility forecasts (annualized)
            forecast_variance = forecast.variance.values[-1, :]
            forecast_volatility = np.sqrt(forecast_variance) / 100  # Convert back from scaled returns
            forecast_volatility_annualized = forecast_volatility * np.sqrt(252)
            
            return {
                'variance_forecast': forecast_variance,
                'volatility_forecast': forecast_volatility,
                'volatility_annualized': forecast_volatility_annualized,
                'forecast_object': forecast
            }
        except Exception as e:
            print(f"Error generating volatility forecast: {e}")
            return None
    
    def rolling_volatility_forecast(self, returns, p=1, q=1, 
                                  train_size=0.8, forecast_horizon=5, step=1):
        """Perform rolling volatility forecasting"""
        n = len(returns)
        train_end = int(n * train_size)
        
        volatility_forecasts = []
        actual_volatility = []
        forecast_dates = []
        
        for i in range(train_end, n - forecast_horizon + 1, step):
            # Training data
            train_data = returns[:i]
            
            try:
                # Fit GARCH model
                model = self.fit_garch_model(train_data, p=p, q=q)
                if model is None:
                    continue
                
                # Generate volatility forecast
                forecast_result = self.forecast_volatility(model, horizon=forecast_horizon)
                if forecast_result is None:
                    continue
                
                # Store first period forecast
                forecast_vol = forecast_result['volatility_annualized'][0]
                actual_vol = returns[i:i+forecast_horizon].std() * np.sqrt(252)
                
                volatility_forecasts.append(forecast_vol)
                actual_volatility.append(actual_vol)
                forecast_dates.append(returns.index[i])
                
            except Exception as e:
                print(f"Error in rolling forecast at step {i}: {e}")
                continue
        
        return {
            'forecasts': volatility_forecasts,
            'actuals': actual_volatility,
            'dates': forecast_dates
        }
    
    def calculate_historical_volatility(self, returns, window=21):
        """Calculate historical volatility"""
        return returns.rolling(window=window).std() * np.sqrt(252)
    
    def plot_volatility_comparison(self, returns, garch_model, historical_volatility, 
                                 forecast_result=None, title="Volatility Comparison"):
        """Plot GARCH volatility vs historical volatility"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot returns
        ax1.plot(returns.index, returns.values, color='blue', alpha=0.7)
        ax1.set_title('Returns')
        ax1.set_ylabel('Returns')
        ax1.grid(True, alpha=0.3)
        
        # Plot volatility
        # GARCH conditional volatility (annualized)
        garch_volatility = np.sqrt(garch_model.conditional_volatility) / 100 * np.sqrt(252)
        
        ax2.plot(returns.index, garch_volatility, label='GARCH Volatility', color='red')
        ax2.plot(historical_volatility.index, historical_volatility.values, 
                label='Historical Volatility (21-day)', color='blue', alpha=0.7)
        
        # Add forecast if available
        if forecast_result is not None:
            forecast_dates = pd.date_range(start=returns.index[-1], periods=len(forecast_result['volatility_annualized'])+1, freq='D')[1:]
            ax2.plot(forecast_dates, forecast_result['volatility_annualized'], 
                    label='Volatility Forecast', color='green', linestyle='--')
        
        ax2.set_title(title)
        ax2.set_ylabel('Annualized Volatility')
        ax2.set_xlabel('Date')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def volatility_clustering_test(self, returns, lags=10):
        """Test for volatility clustering using Ljung-Box test on squared returns"""
        squared_returns = returns ** 2
        
        from statsmodels.stats.diagnostic import acorr_ljungbox
        lb_test = acorr_ljungbox(squared_returns.dropna(), lags=lags, return_df=True)
        
        print("Ljung-Box Test for Volatility Clustering (squared returns):")
        print(lb_test)
        
        # Plot ACF of squared returns
        from statsmodels.graphics.tsaplots import plot_acf
        plt.figure(figsize=(10, 6))
        plot_acf(squared_returns.dropna(), lags=lags)
        plt.title('Autocorrelation of Squared Returns (Volatility Clustering)')
        plt.show()
        
        return lb_test
    
    def leverage_effect_test(self, returns):
        """Test for leverage effect (asymmetric volatility)"""
        # Create positive and negative return indicators
        positive_returns = returns[returns > 0]
        negative_returns = returns[returns < 0]
        
        # Calculate volatility following positive and negative returns
        vol_after_positive = positive_returns.rolling(window=5).std().dropna()
        vol_after_negative = negative_returns.rolling(window=5).std().dropna()
        
        # Statistical test
        from scipy.stats import ttest_ind
        t_stat, p_value = ttest_ind(vol_after_positive.dropna(), 
                                  vol_after_negative.dropna(), 
                                  equal_var=False)
        
        print(f"Leverage Effect Test:")
        print(f"Volatility after positive returns: {vol_after_positive.mean():.6f}")
        print(f"Volatility after negative returns: {vol_after_negative.mean():.6f}")
        print(f"T-statistic: {t_stat:.4f}, p-value: {p_value:.4f}")
        
        if p_value < 0.05:
            print("Significant leverage effect detected")
        else:
            print("No significant leverage effect detected")
        
        return t_stat, p_value
    
    def value_at_risk_garch(self, model, returns, confidence_level=0.05):
        """Calculate Value at Risk using GARCH model"""
        # Get conditional volatility
        conditional_volatility = np.sqrt(model.conditional_volatility) / 100
        
        # Calculate VaR
        if hasattr(model, 'distribution'):
            if model.distribution.name == 'normal':
                z_score = stats.norm.ppf(confidence_level)
            elif model.distribution.name == 't':
                z_score = stats.t.ppf(confidence_level, df=model.distribution._parameters[0])
            else:
                z_score = stats.norm.ppf(confidence_level)
        else:
            z_score = stats.norm.ppf(confidence_level)
        
        var = z_score * conditional_volatility
        
        return var

def demonstrate_garch_modeling():
    """Demonstrate GARCH modeling capabilities"""
    print("GARCH Volatility Modeling Demonstration")
    print("=" * 50)
    
    modeler = GARCHModeler()
    
    # Load sample data
    symbol = 'AAPL'
    stock = yf.Ticker(symbol)
    data = stock.history(period='3y')
    returns = data['Close'].pct_change().dropna()
    
    print(f"Data loaded: {len(returns)} returns")
    
    # Test for volatility clustering
    print("\n1. Testing for volatility clustering...")
    clustering_test = modeler.volatility_clustering_test(returns)
    
    # Test for leverage effect
    print("\n2. Testing for leverage effect...")
    leverage_test = modeler.leverage_effect_test(returns)
    
    # Fit multiple GARCH models
    print("\n3. Fitting multiple GARCH models...")
    orders_to_test = [(1,1), (1,2), (2,1), (2,2)]
    comparison = modeler.fit_multiple_garch_models(returns, orders_to_test)
    
    print("\nGARCH Model Comparison (sorted by AIC):")
    for result in comparison:
        print(f"  GARCH{result['order']}: AIC={result['aic']:.2f}")
    
    # Use best model
    best_model = comparison[0]['model']
    best_order = comparison[0]['order']
    
    print(f"\n4. Using GARCH{best_order} model:")
    print(best_model.summary())
    
    # Generate volatility forecast
    print("\n5. Generating volatility forecasts...")
    forecast_result = modeler.forecast_volatility(best_model, horizon=10)
    
    if forecast_result is not None:
        print("Volatility Forecast (Annualized):")
        for i, vol in enumerate(forecast_result['volatility_annualized']):
            print(f"  Day {i+1}: {vol:.2%}")
    
    # Calculate historical volatility for comparison
    historical_vol = modeler.calculate_historical_volatility(returns, window=21)
    
    # Plot volatility comparison
    print("\n6. Generating volatility plots...")
    modeler.plot_volatility_comparison(
        returns, best_model, historical_vol, forecast_result,
        title=f"GARCH{best_order} Volatility vs Historical Volatility - {symbol}"
    )
    
    # Calculate Value at Risk
    print("\n7. Calculating Value at Risk...")
    var_95 = modeler.value_at_risk_garch(best_model, returns, confidence_level=0.05)
    var_99 = modeler.value_at_risk_garch(best_model, returns, confidence_level=0.01)
    
    print(f"Current 1-day VaR (95%): {var_95.iloc[-1]:.2%}")
    print(f"Current 1-day VaR (99%): {var_99.iloc[-1]:.2%}")
    
    # Rolling volatility forecast
    print("\n8. Performing rolling volatility forecast...")
    rolling_results = modeler.rolling_volatility_forecast(
        returns, p=best_order[0], q=best_order[1], 
        train_size=0.7, forecast_horizon=5, step=5
    )
    
    if len(rolling_results['forecasts']) > 0:
        forecast_accuracy = np.mean((np.array(rolling_results['forecasts']) - np.array(rolling_results['actuals'])) ** 2)
        print(f"Rolling forecast MSE: {forecast_accuracy:.6f}")
    
    return modeler, best_model, returns

if __name__ == "__main__":
    demonstrate_garch_modeling()