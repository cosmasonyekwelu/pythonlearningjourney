import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, TimeSeriesSplit, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.svm import SVR, SVC
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_regression, f_classif
import xgboost as xgb
import lightgbm as lgb
from scipy.stats import randint, uniform
import warnings
warnings.filterwarnings('ignore')

class TradingMLModels:
    def __init__(self):
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.results = {}
        self.feature_importance = {}
        
    def prepare_data(self, data, target_col='Target', test_size=0.2, problem_type='regression'):
        """Prepare data for machine learning"""
        # Separate features and target
        X = data.drop(columns=[target_col])
        y = data[target_col]
        
        # For classification, convert returns to directional moves
        if problem_type == 'classification':
            y = (y > 0).astype(int)  # 1 for positive returns, 0 for negative
        
        # Time-series aware split (no shuffling)
        split_idx = int(len(X) * (1 - test_size))
        self.X_train, self.X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        self.y_train, self.y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        print(f"Data prepared: {len(self.X_train)} train, {len(self.X_test)} test samples")
        print(f"Target distribution - Train: {pd.Series(self.y_train).value_counts().to_dict()}")
        if problem_type == 'classification':
            print(f"Target distribution - Test: {pd.Series(self.y_test).value_counts().to_dict()}")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def create_regression_models(self):
        """Initialize regression models for return prediction"""
        models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=0.1),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'SVR': SVR(kernel='rbf', C=1.0),
            'KNN': KNeighborsRegressor(n_neighbors=5),
            'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42),
            'LightGBM': lgb.LGBMRegressor(n_estimators=100, random_state=42)
        }
        return models
    
    def create_classification_models(self):
        """Initialize classification models for directional prediction"""
        models = {
            'Logistic Regression': LogisticRegression(random_state=42),
            'Random Forest Classifier': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting Classifier': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'SVC': SVC(probability=True, random_state=42),
            'KNN Classifier': KNeighborsClassifier(n_neighbors=5),
            'XGBoost Classifier': xgb.XGBClassifier(n_estimators=100, random_state=42),
            'LightGBM Classifier': lgb.LGBMClassifier(n_estimators=100, random_state=42)
        }
        return models
    
    def evaluate_regression(self, y_true, y_pred, model_name):
        """Evaluate regression model performance"""
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        # Direction accuracy (if predicting returns)
        direction_acc = np.mean((y_true * y_pred) > 0)  # Same sign
        
        results = {
            'MSE': mse,
            'RMSE': np.sqrt(mse),
            'MAE': mae,
            'R2': r2,
            'Direction_Accuracy': direction_acc
        }
        
        print(f"{model_name} Regression Results:")
        print(f"  MSE: {mse:.6f}, RMSE: {np.sqrt(mse):.6f}")
        print(f"  MAE: {mae:.6f}, R²: {r2:.4f}")
        print(f"  Direction Accuracy: {direction_acc:.4f}")
        
        return results
    
    def evaluate_classification(self, y_true, y_pred, y_pred_proba=None, model_name=""):
        """Evaluate classification model performance"""
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        results = {
            'Accuracy': accuracy,
            'Precision': precision,
            'Recall': recall,
            'F1-Score': f1
        }
        
        if y_pred_proba is not None:
            roc_auc = roc_auc_score(y_true, y_pred_proba)
            results['ROC-AUC'] = roc_auc
            print(f"  ROC-AUC: {roc_auc:.4f}")
        
        print(f"{model_name} Classification Results:")
        print(f"  Accuracy: {accuracy:.4f}, Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}, F1-Score: {f1:.4f}")
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        self.plot_confusion_matrix(cm, model_name)
        
        return results
    
    def plot_confusion_matrix(self, cm, model_name):
        """Plot confusion matrix"""
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Down', 'Up'], 
                   yticklabels=['Down', 'Up'])
        plt.title(f'Confusion Matrix - {model_name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.show()
    
    def train_regression_models(self, data, target_col='Target'):
        """Train and compare regression models"""
        print("TRAINING REGRESSION MODELS")
        print("=" * 50)
        
        # Prepare data
        self.prepare_data(data, target_col, problem_type='regression')
        
        models = self.create_regression_models()
        results = {}
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            # Create pipeline with imputation and scaling
            pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler()),
                ('model', model)
            ])
            
            # Train model
            pipeline.fit(self.X_train, self.y_train)
            
            # Predictions
            y_pred = pipeline.predict(self.X_test)
            
            # Evaluate
            model_results = self.evaluate_regression(self.y_test, y_pred, name)
            results[name] = {
                'model': pipeline,
                'predictions': y_pred,
                'metrics': model_results
            }
            
            # Store feature importance for tree-based models
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = pipeline.named_steps['model'].feature_importances_
        
        self.models.update(results)
        self.results.update(results)
        
        # Compare models
        self.compare_regression_models(results)
        
        return results
    
    def train_classification_models(self, data, target_col='Target'):
        """Train and compare classification models"""
        print("TRAINING CLASSIFICATION MODELS")
        print("=" * 50)
        
        # Prepare data
        self.prepare_data(data, target_col, problem_type='classification')
        
        models = self.create_classification_models()
        results = {}
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            # Create pipeline
            pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler()),
                ('model', model)
            ])
            
            # Train model
            pipeline.fit(self.X_train, self.y_train)
            
            # Predictions
            y_pred = pipeline.predict(self.X_test)
            y_pred_proba = pipeline.predict_proba(self.X_test)[:, 1] if hasattr(pipeline, 'predict_proba') else None
            
            # Evaluate
            model_results = self.evaluate_classification(self.y_test, y_pred, y_pred_proba, name)
            results[name] = {
                'model': pipeline,
                'predictions': y_pred,
                'probabilities': y_pred_proba,
                'metrics': model_results
            }
            
            # Store feature importance
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = pipeline.named_steps['model'].feature_importances_
        
        self.models.update(results)
        self.results.update(results)
        
        # Compare models
        self.compare_classification_models(results)
        
        return results
    
    def compare_regression_models(self, results):
        """Compare performance of regression models"""
        metrics_df = pd.DataFrame({
            name: result['metrics'] for name, result in results.items()
        }).T
        
        # Sort by R2 score
        metrics_df = metrics_df.sort_values('R2', ascending=False)
        
        print("\nREGRESSION MODEL COMPARISON (Sorted by R²):")
        print(metrics_df.round(4))
        
        # Plot comparison
        self.plot_model_comparison(metrics_df, 'R2', 'R² Score Comparison')
        self.plot_model_comparison(metrics_df, 'Direction_Accuracy', 'Direction Accuracy Comparison')
        
        return metrics_df
    
    def compare_classification_models(self, results):
        """Compare performance of classification models"""
        metrics_df = pd.DataFrame({
            name: result['metrics'] for name, result in results.items()
        }).T
        
        # Sort by accuracy
        metrics_df = metrics_df.sort_values('Accuracy', ascending=False)
        
        print("\nCLASSIFICATION MODEL COMPARISON (Sorted by Accuracy):")
        print(metrics_df.round(4))
        
        # Plot comparison
        self.plot_model_comparison(metrics_df, 'Accuracy', 'Accuracy Comparison')
        
        if 'ROC-AUC' in metrics_df.columns:
            self.plot_model_comparison(metrics_df, 'ROC-AUC', 'ROC-AUC Comparison')
        
        return metrics_df
    
    def plot_model_comparison(self, metrics_df, metric, title):
        """Plot model comparison for a specific metric"""
        plt.figure(figsize=(10, 6))
        metrics_df[metric].sort_values(ascending=True).plot(kind='barh')
        plt.title(title, fontweight='bold')
        plt.xlabel(metric)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def random_forest_tutorial(self, data, target_col='Target'):
        """Tutorial: Train Random Forest for directional prediction"""
        print("RANDOM FOREST TUTORIAL")
        print("=" * 40)
        
        # Prepare data for classification
        self.prepare_data(data, target_col, problem_type='classification')
        
        # Create feature matrix with lagged features
        feature_cols = [col for col in data.columns if 'Lag' in col or 'Roll' in col or 'RSI' in col or 'MACD' in col]
        feature_cols = [col for col in feature_cols if col in self.X_train.columns]
        
        print(f"Using {len(feature_cols)} features for Random Forest")
        
        # Train Random Forest
        rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42
        )
        
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('model', rf_model)
        ])
        
        pipeline.fit(self.X_train[feature_cols], self.y_train)
        
        # Predictions
        y_pred = pipeline.predict(self.X_test[feature_cols])
        y_pred_proba = pipeline.predict_proba(self.X_test[feature_cols])[:, 1]
        
        # Evaluate
        results = self.evaluate_classification(self.y_test, y_pred, y_pred_proba, "Random Forest Tutorial")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': pipeline.named_steps['model'].feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))
        
        # Plot feature importance
        plt.figure(figsize=(10, 8))
        top_features = feature_importance.head(15)
        plt.barh(range(len(top_features)), top_features['importance'])
        plt.yticks(range(len(top_features)), top_features['feature'])
        plt.xlabel('Feature Importance')
        plt.title('Random Forest - Top 15 Feature Importance', fontweight='bold')
        plt.gca().invert_yaxis()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
        
        return pipeline, results, feature_importance

class HyperparameterOptimizer:
    """Class for hyperparameter optimization"""
    
    def __init__(self):
        self.best_models = {}
        self.optimization_results = {}
    
    def grid_search_optimization(self, model, param_grid, X_train, y_train, cv=5, scoring='accuracy'):
        """Perform grid search optimization"""
        print(f"Performing Grid Search for {model.__class__.__name__}...")
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=cv)
        
        grid_search = GridSearchCV(
            estimator=model,
            param_grid=param_grid,
            cv=tscv,
            scoring=scoring,
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best score: {grid_search.best_score_:.4f}")
        
        return grid_search
    
    def random_forest_optimization(self, X_train, y_train):
        """Optimize Random Forest hyperparameters"""
        rf = RandomForestClassifier(random_state=42)
        
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2']
        }
        
        grid_search = self.grid_search_optimization(
            rf, param_grid, X_train, y_train, scoring='f1'
        )
        
        self.best_models['Random Forest'] = grid_search.best_estimator_
        self.optimization_results['Random Forest'] = grid_search
        
        return grid_search
    
    def xgboost_optimization(self, X_train, y_train):
        """Optimize XGBoost hyperparameters"""
        xgb_model = xgb.XGBClassifier(random_state=42)
        
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.1, 0.2],
            'subsample': [0.8, 0.9, 1.0],
            'colsample_bytree': [0.8, 0.9, 1.0]
        }
        
        grid_search = self.grid_search_optimization(
            xgb_model, param_grid, X_train, y_train, scoring='f1'
        )
        
        self.best_models['XGBoost'] = grid_search.best_estimator_
        self.optimization_results['XGBoost'] = grid_search
        
        return grid_search
    
    def compare_optimized_models(self, X_test, y_test):
        """Compare performance of optimized models"""
        results = {}
        
        for name, model in self.best_models.items():
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            results[name] = {
                'Accuracy': accuracy,
                'F1-Score': f1
            }
            
            print(f"{name} - Accuracy: {accuracy:.4f}, F1-Score: {f1:.4f}")
        
        return results

# Challenge: GridSearchCV optimization
def grid_search_challenge(data, target_col='Target'):
    """Challenge: Perform comprehensive hyperparameter optimization"""
    print("GRIDSEARCHCV OPTIMIZATION CHALLENGE")
    print("=" * 50)
    
    # Prepare data
    ml_model = TradingMLModels()
    X_train, X_test, y_train, y_test = ml_model.prepare_data(
        data, target_col, problem_type='classification'
    )
    
    # Initialize optimizer
    optimizer = HyperparameterOptimizer()
    
    # Optimize models
    print("\n1. RANDOM FOREST OPTIMIZATION")
    rf_results = optimizer.random_forest_optimization(X_train, y_train)
    
    print("\n2. XGBOOST OPTIMIZATION")
    xgb_results = optimizer.xgboost_optimization(X_train, y_train)
    
    # Compare optimized models
    print("\nOPTIMIZED MODEL COMPARISON:")
    comparison = optimizer.compare_optimized_models(X_test, y_test)
    
    # Compare with baseline
    print("\nBASELINE COMPARISON:")
    baseline_models = ml_model.create_classification_models()
    baseline_rf = baseline_models['Random Forest Classifier']
    baseline_rf.fit(X_train, y_train)
    baseline_pred = baseline_rf.predict(X_test)
    baseline_acc = accuracy_score(y_test, baseline_pred)
    baseline_f1 = f1_score(y_test, baseline_pred)
    
    print(f"Baseline Random Forest - Accuracy: {baseline_acc:.4f}, F1-Score: {baseline_f1:.4f}")
    
    # Improvement analysis
    optimized_rf_acc = comparison['Random Forest']['Accuracy']
    improvement = (optimized_rf_acc - baseline_acc) / baseline_acc * 100
    
    print(f"\nOptimization Improvement: {improvement:.2f}%")
    
    return optimizer, comparison

if __name__ == "__main__":
    # Example usage with synthetic data
    print("MACHINE LEARNING FOR TRADING MODELS")
    print("=" * 50)
    
    # Generate sample data (in practice, use FeatureEngineer from Day 52)
    def generate_sample_data(n_samples=1000, n_features=20):
        """Generate sample financial data for demonstration"""
        np.random.seed(42)
        
        # Create feature matrix
        X = np.random.randn(n_samples, n_features)
        
        # Create target with some predictability
        true_weights = np.random.randn(n_features)
        true_weights[np.abs(true_weights) < 0.5] = 0  # Sparse weights
        
        returns = X @ true_weights + np.random.randn(n_samples) * 0.1
        
        # Create DataFrame
        feature_cols = [f'Feature_{i}' for i in range(n_features)]
        data = pd.DataFrame(X, columns=feature_cols)
        data['Target'] = returns
        
        # Add some lag features
        for lag in [1, 2, 3]:
            data[f'Returns_Lag_{lag}'] = data['Target'].shift(lag)
        
        data = data.dropna()
        
        return data
    
    # Generate sample data
    sample_data = generate_sample_data(1000, 20)
    
    # Initialize ML models
    ml_trader = TradingMLModels()
    
    # Train regression models
    regression_results = ml_trader.train_regression_models(sample_data)
    
    # Train classification models  
    classification_results = ml_trader.train_classification_models(sample_data)
    
    # Random Forest tutorial
    rf_pipeline, rf_results, feature_importance = ml_trader.random_forest_tutorial(sample_data)
    
    # GridSearchCV challenge
    optimizer, comparison = grid_search_challenge(sample_data)