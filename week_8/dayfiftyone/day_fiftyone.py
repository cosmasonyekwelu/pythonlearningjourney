import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import yfinance as yf
from arch import arch_model
import warnings
warnings.filterwarnings('ignore')


class StatisticalAnalysis:
    def __init__(self):
        self.data = None
        self.returns = None

    def load_data(self, ticker='SPY', start_date='2020-01-01'):
        """Load financial data"""
        self.data = yf.download(ticker, start=start_date)
        self.data['Returns'] = self.data['Adj Close'].pct_change().dropna()
        self.returns = self.data['Returns']
        return self.data

    def stationarity_test(self, series=None, name="Price"):
        """Perform Augmented Dickey-Fuller test for stationarity"""
        if series is None:
            series = self.data['Adj Close']

        result = adfuller(series.dropna())

        print(f"\n{name} Stationarity Test (ADF):")
        print(f"ADF Statistic: {result[0]:.6f}")
        print(f"p-value: {result[1]:.6f}")
        print(f"Critical Values:")
        for key, value in result[4].items():
            print(f"  {key}: {value:.3f}")

        if result[1] <= 0.05:
            print("✅ Series is STATIONARY (reject null hypothesis)")
        else:
            print("❌ Series is NON-STATIONARY (fail to reject null hypothesis)")

        return result

    def normality_tests(self, series=None):
        """Perform normality tests including Shapiro-Wilk and Q-Q plots"""
        if series is None:
            series = self.returns

        series_clean = series.dropna()

        # Shapiro-Wilk test
        shapiro_stat, shapiro_p = stats.shapiro(series_clean)

        # Jarque-Bera test
        jb_stat, jb_p, skew, kurtosis = self.jarque_bera_test(series_clean)

        print("\nNormality Tests:")
        print(
            f"Shapiro-Wilk Test: statistic={shapiro_stat:.4f}, p-value={shapiro_p:.4f}")
        print(f"Jarque-Bera Test: statistic={jb_stat:.4f}, p-value={jb_p:.4f}")
        print(f"Skewness: {skew:.4f}")
        print(f"Kurtosis: {kurtosis:.4f}")

        # Plot Q-Q plot
        self.plot_qq(series_clean)

        return {
            'shapiro': (shapiro_stat, shapiro_p),
            'jarque_bera': (jb_stat, jb_p),
            'skewness': skew,
            'kurtosis': kurtosis
        }

    def jarque_bera_test(self, series):
        """Calculate Jarque-Bera test statistic"""
        n = len(series)
        skewness = stats.skew(series)
        # Fisher=False gives actual kurtosis
        kurt = stats.kurtosis(series, fisher=False)

        jb_stat = n / 6 * (skewness**2 + (kurt - 3)**2 / 4)
        jb_p = 1 - stats.chi2.cdf(jb_stat, 2)

        return jb_stat, jb_p, skewness, kurt

    def plot_qq(self, series):
        """Plot Q-Q plot for normality assessment"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Q-Q plot
        stats.probplot(series, dist="norm", plot=ax1)
        ax1.set_title('Q-Q Plot - Normality Check', fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Histogram with normal overlay
        ax2.hist(series, bins=50, density=True, alpha=0.7, edgecolor='black')
        x = np.linspace(series.min(), series.max(), 100)
        ax2.plot(x, stats.norm.pdf(x, series.mean(), series.std()),
                 'r-', linewidth=2, label='Normal Distribution')
        ax2.set_title('Returns Distribution vs Normal', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def autocorrelation_analysis(self, lags=40):
        """Analyze autocorrelation and partial autocorrelation"""
        returns_clean = self.returns.dropna()

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

        # ACF plot
        plot_acf(returns_clean, lags=lags, ax=ax1, alpha=0.05)
        ax1.set_title('Autocorrelation Function (ACF)', fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # PACF plot
        plot_pacf(returns_clean, lags=lags, ax=ax2, alpha=0.05)
        ax2.set_title('Partial Autocorrelation Function (PACF)',
                      fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # Autocorrelation coefficients table
        acf_values = acf(returns_clean, nlags=lags)
        pacf_values = pacf(returns_clean, nlags=lags)

        # Significant lags (outside 95% confidence interval)
        significant_acf = np.where(
            np.abs(acf_values) > 1.96 / np.sqrt(len(returns_clean)))[0]
        significant_pacf = np.where(
            np.abs(pacf_values) > 1.96 / np.sqrt(len(returns_clean)))[0]

        ax3.axis('off')
        table_text = f"Significant ACF lags: {list(significant_acf)}\nSignificant PACF lags: {list(significant_pacf)}"
        ax3.text(0.1, 0.5, table_text, fontsize=12, va='center', ha='left')
        ax3.set_title('Significant Autocorrelation Lags', fontweight='bold')

        plt.tight_layout()
        plt.show()

        return acf_values, pacf_values

    def volatility_modeling(self, p=1, q=1):
        """Implement GARCH model for volatility clustering"""
        returns_clean = self.returns.dropna() * 100  # Scale for better convergence

        # Fit GARCH model
        model = arch_model(returns_clean, vol='Garch', p=p, q=q)
        fitted_model = model.fit(disp='off')

        print("\nGARCH Model Results:")
        print(fitted_model.summary())

        # Plot conditional volatility
        conditional_vol = fitted_model.conditional_volatility / 100  # Rescale back

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Returns with GARCH volatility
        ax1.plot(self.returns.index, self.returns,
                 alpha=0.7, linewidth=0.5, label='Returns')
        ax1.plot(self.returns.index[-len(conditional_vol):], conditional_vol,
                 'r-', linewidth=1, label='GARCH Conditional Volatility')
        ax1.set_title('Returns and GARCH Volatility', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Rolling volatility vs GARCH
        rolling_vol = self.returns.rolling(window=21).std()
        ax2.plot(rolling_vol.index, rolling_vol, 'g-',
                 linewidth=1, label='21-day Rolling Vol')
        ax2.plot(self.returns.index[-len(conditional_vol):], conditional_vol,
                 'r-', linewidth=1, label='GARCH Conditional Vol')
        ax2.set_title('GARCH vs Rolling Volatility', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        return fitted_model

    def hypothesis_testing(self, test_returns=None, benchmark_returns=None):
        """Perform statistical hypothesis tests"""
        if test_returns is None:
            test_returns = self.returns

        if benchmark_returns is None:
            # Create synthetic benchmark (market returns)
            benchmark_returns = test_returns * 0.8 + \
                np.random.normal(0, test_returns.std() *
                                 0.2, len(test_returns))

        # One-sample t-test (test if mean return is zero)
        t_stat, p_value = stats.ttest_1samp(test_returns.dropna(), 0)

        # Two-sample t-test (compare two return series)
        t_stat_2sample, p_value_2sample = stats.ttest_ind(test_returns.dropna(),
                                                          benchmark_returns.dropna())

        # Variance ratio test (random walk test)
        vr_stat, vr_p_value = self.variance_ratio_test(test_returns)

        print("\nHypothesis Testing Results:")
        print(
            f"One-sample t-test (mean = 0): t-stat={t_stat:.4f}, p-value={p_value:.4f}")
        print(
            f"Two-sample t-test (equal means): t-stat={t_stat_2sample:.4f}, p-value={p_value_2sample:.4f}")
        print(
            f"Variance Ratio Test (random walk): statistic={vr_stat:.4f}, p-value={vr_p_value:.4f}")

        # Confidence intervals
        confidence_interval = stats.t.interval(0.95, len(test_returns)-1,
                                               loc=test_returns.mean(),
                                               scale=test_returns.std()/np.sqrt(len(test_returns)))
        print(
            f"95% Confidence Interval for Mean Return: [{confidence_interval[0]:.6f}, {confidence_interval[1]:.6f}]")

        return {
            'one_sample_test': (t_stat, p_value),
            'two_sample_test': (t_stat_2sample, p_value_2sample),
            'variance_ratio': (vr_stat, vr_p_value),
            'confidence_interval': confidence_interval
        }

    def variance_ratio_test(self, returns, lag=2):
        """Variance ratio test for random walk hypothesis"""
        returns_clean = returns.dropna()
        n = len(returns_clean)

        # Variance of 1-period returns
        var_1 = returns_clean.var()

        # Variance of k-period returns
        k_period_returns = returns_clean.rolling(window=lag).sum().dropna()
        var_k = k_period_returns.var()

        # Variance ratio
        vr = var_k / (lag * var_1)

        # Test statistic (asymptotically normal)
        vr_stat = (vr - 1) / np.sqrt(2 * (2 * lag - 1)
                                     * (lag - 1) / (3 * lag * n))
        vr_p_value = 2 * (1 - stats.norm.cdf(np.abs(vr_stat)))

        return vr_stat, vr_p_value

    def risk_return_metrics(self):
        """Calculate comprehensive risk-return statistics"""
        returns_clean = self.returns.dropna()
        cumulative_returns = (1 + returns_clean).cumprod()

        # Basic metrics
        total_return = cumulative_returns.iloc[-1] - 1
        annual_return = (1 + total_return) ** (252 / len(returns_clean)) - 1
        annual_volatility = returns_clean.std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility if annual_volatility != 0 else 0

        # Drawdown analysis
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # Higher moments
        skewness = stats.skew(returns_clean)
        kurtosis = stats.kurtosis(
            returns_clean, fisher=False)  # Pearson kurtosis

        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns_clean, 5)

        # Conditional VaR (Expected Shortfall)
        cvar_95 = returns_clean[returns_clean <= var_95].mean()

        print("\nRisk-Return Metrics:")
        print(f"Total Return: {total_return:.2%}")
        print(f"Annual Return: {annual_return:.2%}")
        print(f"Annual Volatility: {annual_volatility:.2%}")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"Max Drawdown: {max_drawdown:.2%}")
        print(f"Skewness: {skewness:.4f}")
        print(f"Kurtosis: {kurtosis:.4f}")
        print(f"VaR (95%): {var_95:.2%}")
        print(f"CVaR (95%): {cvar_95:.2%}")

        return {
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'var_95': var_95,
            'cvar_95': cvar_95
        }

    def run_complete_analysis(self, ticker='SPY'):
        """Run complete statistical analysis"""
        print(f"COMPLETE STATISTICAL ANALYSIS FOR {ticker}")
        print("=" * 60)

        self.load_data(ticker)

        # Stationarity tests
        print("\n1. STATIONARITY ANALYSIS")
        self.stationarity_test(self.data['Adj Close'], "Price")
        self.stationarity_test(self.returns, "Returns")

        # Normality tests
        print("\n2. NORMALITY ANALYSIS")
        self.normality_tests()

        # Autocorrelation analysis
        print("\n3. AUTOCORRELATION ANALYSIS")
        self.autocorrelation_analysis()

        # Volatility modeling
        print("\n4. VOLATILITY MODELING")
        self.volatility_modeling()

        # Hypothesis testing
        print("\n5. HYPOTHESIS TESTING")
        self.hypothesis_testing()

        # Risk-return metrics
        print("\n6. RISK-RETURN METRICS")
        self.risk_return_metrics()

        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")

# Challenge: Volatility clustering visualization and GARCH comparison


def volatility_clustering_challenge():
    """Challenge: Implement advanced volatility analysis"""
    analyzer = StatisticalAnalysis()
    analyzer.load_data('SPY')

    # Compare different GARCH models
    print("GARCH MODEL COMPARISON")
    print("=" * 50)

    # Fit different GARCH specifications
    specifications = [(1, 1), (1, 2), (2, 1), (2, 2)]

    for p, q in specifications:
        print(f"\nGARCH({p},{q}) Model:")
        try:
            model = analyzer.volatility_modeling(p, q)
            print(f"AIC: {model.aic:.2f}")
            print(f"BIC: {model.bic:.2f}")
        except Exception as e:
            print(f"Error fitting GARCH({p},{q}): {e}")

    # Volatility clustering visualization
    returns = analyzer.returns.dropna()

    # Calculate rolling volatility
    rolling_vol = returns.rolling(window=21).std()

    # Identify high and low volatility periods
    vol_median = rolling_vol.median()
    high_vol_periods = returns[rolling_vol > vol_median]
    low_vol_periods = returns[rolling_vol < vol_median]

    print(f"\nVolatility Clustering Analysis:")
    print(f"High volatility periods: {len(high_vol_periods)} days")
    print(f"Low volatility periods: {len(low_vol_periods)} days")
    print(f"High vol mean return: {high_vol_periods.mean():.6f}")
    print(f"Low vol mean return: {low_vol_periods.mean():.6f}")

    # Plot volatility regimes
    plt.figure(figsize=(12, 8))

    plt.subplot(2, 1, 1)
    plt.plot(returns.index, returns, 'b-', alpha=0.3, linewidth=0.5)
    plt.scatter(high_vol_periods.index, high_vol_periods, color='red',
                alpha=0.6, s=10, label='High Volatility')
    plt.scatter(low_vol_periods.index, low_vol_periods, color='green',
                alpha=0.6, s=10, label='Low Volatility')
    plt.title('Volatility Clustering in Returns', fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 1, 2)
    plt.plot(rolling_vol.index, rolling_vol, 'purple', linewidth=1.5)
    plt.axhline(y=vol_median, color='red',
                linestyle='--', label='Median Volatility')
    plt.title('Rolling 21-day Volatility', fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Run complete analysis
    analyzer = StatisticalAnalysis()
    analyzer.run_complete_analysis('SPY')

    # Run challenge
    volatility_clustering_challenge()
