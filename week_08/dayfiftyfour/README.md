# Day 54: Model Evaluation & Interpretation

**Date:** November 14, 2025

## Learning Objective
To implement rigorous validation techniques for time-series models and use explainable AI (XAI) to interpret complex model predictions.

## Concepts Covered
- **Walk-Forward Validation**: Simulating how a model would perform in a live environment by continuously retraining as new data arrives.
- **Time-Series Cross-Validation**: Ensuring the training data always precedes the validation data to prevent "look-ahead" bias.
- **SHAP (SHapley Additive exPlanations)**: Calculating the contribution of each feature to an individual prediction.
- **Permutation Importance**: Measuring feature importance by randomly shuffling values and observing the drop in accuracy.
- **Overfitting Analysis**: Using learning curves to identify when a model is memorizing the noise in the data.

## Code Explanation
The `day_fiftyfour.py` script implements the `ModelEvaluator` class:
- **`walk_forward_validation()`**: A robust alternative to standard k-fold CV that preserves temporal order.
- **`shap_analysis()`**: Uses the `shap` library to create "force plots" and "dependence plots" for model transparency.
- **`detailed_confusion_analysis()`**: Breaks down True Positives, False Positives (over-trading), and False Negatives (missed opportunities).
- **`plot_roc_curves()`**: Visualizes the trade-off between sensitivity and specificity across different models.

## How to Run
1. Install requirements: `pip install pandas numpy matplotlib seaborn scikit-learn shap`
2. Run the evaluation suite:
```bash
python week_08/dayfiftyfour/day_fiftyfour.py
```

## Reflection
"Black box" models are dangerous in trading. Understanding *why* a model expects the market to go up—for example, due to a specific RSI level combined with volume spikes—allows a trader to have confidence during periods of high volatility.
