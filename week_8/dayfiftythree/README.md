# Day 53: Machine Learning Models (Scikit-learn)

## Overview

Train, tune, and compare machine learning algorithms for market prediction.

## Models Implemented

### Regression Models (Return Prediction)

- **Linear Models**: Linear Regression, Ridge, Lasso
- **Tree-based**: Random Forest, Gradient Boosting, XGBoost, LightGBM
- **Other**: SVR, K-Nearest Neighbors

### Classification Models (Direction Prediction)

- **Linear**: Logistic Regression
- **Tree-based**: Random Forest, Gradient Boosting, XGBoost, LightGBM
- **Other**: SVM, K-Nearest Neighbors

## Key Features

### 1. Problem Framing

- **Regression**: Predict exact return values
- **Classification**: Predict directional movement (up/down)

### 2. Model Pipelines

- Automated data preprocessing
- Handling missing values
- Feature scaling
- Consistent evaluation framework

### 3. Comprehensive Evaluation

**Regression Metrics**:

- MSE, RMSE, MAE, R²
- Direction accuracy

**Classification Metrics**:

- Accuracy, Precision, Recall, F1-Score
- ROC-AUC, Confusion Matrix

### 4. Feature Importance

- Tree-based model interpretability
- Identification of most predictive features
- Visualization of feature contributions

## Tutorial: Random Forest Classifier

The script includes a detailed tutorial for:

1. Feature selection for directional prediction
2. Random Forest training with appropriate parameters
3. Feature importance analysis
4. Model interpretation and validation

## Challenge: Hyperparameter Optimization

### GridSearchCV Implementation

- **Time-series aware cross-validation**: Prevents data leakage
- **Comprehensive parameter grids**: Multiple algorithms
- **Performance comparison**: Baseline vs optimized models
- **Improvement quantification**: Measurable performance gains

### Optimization Techniques

1. **Grid Search**: Exhaustive parameter search
2. **Randomized Search**: Efficient for large parameter spaces
3. **Bayesian Optimization**: Advanced technique for complex spaces

## Key Insights

1. **Algorithm Performance**: Tree-based models often outperform linear models
2. **Hyperparameter Importance**: Proper tuning significantly improves performance
3. **Feature Selection**: Not all features are equally important
4. **Evaluation Rigor**: Time-series cross-validation is crucial

## Usage

```python
# Initialize and train models
ml_trader = TradingMLModels()

# Regression analysis
regression_results = ml_trader.train_regression_models(data)

# Classification analysis
classification_results = ml_trader.train_classification_models(data)

# Hyperparameter optimization
optimizer = HyperparameterOptimizer()
optimized_models = optimizer.random_forest_optimization(X_train, y_train)
```
