import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.inspection import permutation_importance
import shap
import warnings
warnings.filterwarnings('ignore')


class ModelEvaluator:
    def __init__(self):
        self.validation_results = {}
        self.feature_importance_data = {}

    def time_series_cross_validation(self, model, X, y, n_splits=5):
        """Implement time-series aware cross-validation"""
        tscv = TimeSeriesSplit(n_splits=n_splits)
        cv_scores = {
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1': [],
            'roc_auc': []
        }

        print(
            f"Performing Time Series Cross-Validation ({n_splits} splits)...")

        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            # Train model
            model.fit(X_train, y_train)

            # Predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(
                model, 'predict_proba') else None

            # Calculate metrics
            cv_scores['accuracy'].append(accuracy_score(y_test, y_pred))
            cv_scores['precision'].append(
                precision_score(y_test, y_pred, zero_division=0))
            cv_scores['recall'].append(
                recall_score(y_test, y_pred, zero_division=0))
            cv_scores['f1'].append(f1_score(y_test, y_pred, zero_division=0))

            if y_pred_proba is not None:
                cv_scores['roc_auc'].append(
                    roc_auc_score(y_test, y_pred_proba))

            print(
                f"Fold {fold + 1}: Accuracy = {cv_scores['accuracy'][-1]:.4f}")

        # Calculate mean and std of scores
        results = {}
        for metric, scores in cv_scores.items():
            if scores:  # Check if list is not empty
                results[f'CV_{metric}_mean'] = np.mean(scores)
                results[f'CV_{metric}_std'] = np.std(scores)

        print("\nCross-Validation Results:")
        for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
            if f'CV_{metric}_mean' in results:
                print(f"  {metric.upper()}: {results[f'CV_{metric}_mean']:.4f} (±{
                      results[f'CV_{metric}_std']:.4f})")

        return results, cv_scores

    def walk_forward_validation(self, model, X, y, train_size=0.7, step_size=1):
        """Implement walk-forward validation for time series"""
        n_total = len(X)
        n_train = int(n_total * train_size)

        scores = {
            'accuracy': [], 'precision': [], 'recall': [], 'f1': [], 'roc_auc': []
        }

        print("Performing Walk-Forward Validation...")

        for i in range(n_train, n_total, step_size):
            # Expand training set or use rolling window
            X_train, X_test = X.iloc[:i], X.iloc[i:i+step_size]
            y_train, y_test = y.iloc[:i], y.iloc[i:i+step_size]

            if len(X_test) == 0:
                break

            # Retrain model
            model.fit(X_train, y_train)

            # Predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(
                model, 'predict_proba') else None

            # Store scores
            scores['accuracy'].append(accuracy_score(y_test, y_pred))
            scores['precision'].append(
                precision_score(y_test, y_pred, zero_division=0))
            scores['recall'].append(recall_score(
                y_test, y_pred, zero_division=0))
            scores['f1'].append(f1_score(y_test, y_pred, zero_division=0))

            if y_pred_proba is not None:
                scores['roc_auc'].append(roc_auc_score(y_test, y_pred_proba))

        # Calculate summary statistics
        results = {}
        for metric, values in scores.items():
            if values:
                results[f'WF_{metric}_mean'] = np.mean(values)
                results[f'WF_{metric}_std'] = np.std(values)

        print("\nWalk-Forward Validation Results:")
        for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
            if f'WF_{metric}_mean' in results:
                print(f"  {metric.upper()}: {results[f'WF_{metric}_mean']:.4f} (±{
                      results[f'WF_{metric}_std']:.4f})")

        return results, scores

    def detailed_confusion_analysis(self, y_true, y_pred, model_name=""):
        """Perform detailed confusion matrix analysis"""
        cm = confusion_matrix(y_true, y_pred)

        # Calculate metrics from confusion matrix
        tn, fp, fn, tp = cm.ravel()

        accuracy = (tp + tn) / (tp + tn + fp + fn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / \
            (precision + recall) if (precision + recall) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

        print(f"\nDetailed Confusion Analysis - {model_name}:")
        print(f"True Positives: {tp}, False Positives: {fp}")
        print(f"False Negatives: {fn}, True Negatives: {tn}")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall (Sensitivity): {recall:.4f}")
        print(f"Specificity: {specificity:.4f}")
        print(f"F1-Score: {f1:.4f}")

        # Plot enhanced confusion matrix
        plt.figure(figsize=(10, 8))

        plt.subplot(2, 2, 1)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Down', 'Up'],
                    yticklabels=['Down', 'Up'])
        plt.title(f'Confusion Matrix - {model_name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')

        # Metrics comparison
        plt.subplot(2, 2, 2)
        metrics = ['Precision', 'Recall', 'Specificity', 'F1-Score']
        values = [precision, recall, specificity, f1]
        plt.bar(metrics, values, color=['blue', 'green', 'orange', 'red'])
        plt.title('Performance Metrics')
        plt.xticks(rotation=45)
        plt.ylim(0, 1)
        plt.grid(True, alpha=0.3)

        # Class distribution
        plt.subplot(2, 2, 3)
        class_dist = pd.Series(y_true).value_counts()
        plt.pie(class_dist.values, labels=['Down', 'Up'], autopct='%1.1f%%',
                colors=['lightcoral', 'lightgreen'])
        plt.title('True Class Distribution')

        # Prediction distribution
        plt.subplot(2, 2, 4)
        pred_dist = pd.Series(y_pred).value_counts()
        plt.pie(pred_dist.values, labels=['Down', 'Up'], autopct='%1.1f%%',
                colors=['lightcoral', 'lightgreen'])
        plt.title('Predicted Class Distribution')

        plt.tight_layout()
        plt.show()

        return {
            'confusion_matrix': cm,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'specificity': specificity,
            'f1': f1
        }

    def plot_roc_curves(self, models_results, X_test, y_test):
        """Plot ROC curves for multiple models"""
        plt.figure(figsize=(10, 8))

        from sklearn.metrics import roc_curve

        for model_name, results in models_results.items():
            if 'probabilities' in results and results['probabilities'] is not None:
                fpr, tpr, _ = roc_curve(y_test, results['probabilities'])
                roc_auc = roc_auc_score(y_test, results['probabilities'])

                plt.plot(fpr, tpr, label=f'{model_name} (AUC = {roc_auc:.3f})')

        plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curves - Model Comparison', fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def permutation_feature_importance(self, model, X_test, y_test, n_repeats=10):
        """Calculate permutation feature importance"""
        print("Calculating Permutation Feature Importance...")

        result = permutation_importance(
            model, X_test, y_test,
            n_repeats=n_repeats,
            random_state=42,
            n_jobs=-1
        )

        importance_df = pd.DataFrame({
            'feature': X_test.columns,
            'importance_mean': result.importances_mean,
            'importance_std': result.importances_std
        }).sort_values('importance_mean', ascending=False)

        print("\nTop 10 Features by Permutation Importance:")
        print(importance_df.head(10))

        # Plot feature importance
        plt.figure(figsize=(10, 8))
        top_features = importance_df.head(15)

        y_pos = np.arange(len(top_features))
        plt.barh(y_pos, top_features['importance_mean'],
                 xerr=top_features['importance_std'], alpha=0.7)
        plt.yticks(y_pos, top_features['feature'])
        plt.xlabel('Permutation Importance')
        plt.title('Permutation Feature Importance', fontweight='bold')
        plt.gca().invert_yaxis()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

        self.feature_importance_data['permutation'] = importance_df
        return importance_df

    def shap_analysis(self, model, X_test, model_name=""):
        """Perform SHAP analysis for model interpretability"""
        print(f"Performing SHAP Analysis for {model_name}...")

        # Initialize SHAP explainer
        if hasattr(model, 'predict_proba'):
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_test)

            # For binary classification, use values for class 1
            if isinstance(shap_values, list) and len(shap_values) == 2:
                shap_values = shap_values[1]
        else:
            explainer = shap.Explainer(model, X_test)
            shap_values = explainer(X_test)

        # Summary plot
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X_test, show=False)
        plt.title(f'SHAP Summary Plot - {model_name}', fontweight='bold')
        plt.tight_layout()
        plt.show()

        # Feature importance from SHAP
        shap_importance = pd.DataFrame({
            'feature': X_test.columns,
            'shap_importance': np.abs(shap_values).mean(axis=0)
        }).sort_values('shap_importance', ascending=False)

        print(f"\nTop 10 Features by SHAP Importance ({model_name}):")
        print(shap_importance.head(10))

        # Store results
        self.feature_importance_data[f'shap_{model_name}'] = shap_importance

        return shap_importance, explainer

    def compare_feature_importance_methods(self, model, X_test, y_test, model_name=""):
        """Compare different feature importance methods"""
        print(f"COMPARING FEATURE IMPORTANCE METHODS - {model_name}")
        print("=" * 50)

        # 1. Permutation importance
        perm_importance = self.permutation_feature_importance(
            model, X_test, y_test)

        # 2. SHAP importance
        shap_importance, explainer = self.shap_analysis(
            model, X_test, model_name)

        # 3. Built-in feature importance (if available)
        builtin_importance = None
        if hasattr(model, 'feature_importances_'):
            builtin_importance = pd.DataFrame({
                'feature': X_test.columns,
                'builtin_importance': model.feature_importances_
            }).sort_values('builtin_importance', ascending=False)

            print(f"\nTop 10 Features by Built-in Importance ({model_name}):")
            print(builtin_importance.head(10))

        # Compare top features across methods
        comparison_data = []

        for method_name, importance_df in [
            ('Permutation', perm_importance),
            ('SHAP', shap_importance),
            ('Built-in', builtin_importance)
        ]:
            if importance_df is not None:
                top_features = importance_df.head(10)['feature'].tolist()
                comparison_data.append({
                    'Method': method_name,
                    'Top_Features': top_features
                })

        # Create comparison plot
        self.plot_importance_comparison(comparison_data, model_name)

        return {
            'permutation': perm_importance,
            'shap': shap_importance,
            'builtin': builtin_importance
        }

    def plot_importance_comparison(self, comparison_data, model_name):
        """Plot comparison of feature importance across methods"""
        # Create a set of all top features
        all_features = set()
        for data in comparison_data:
            all_features.update(data['Top_Features'])

        # Create ranking matrix
        feature_rankings = {}
        for feature in all_features:
            rankings = []
            for data in comparison_data:
                if feature in data['Top_Features']:
                    rankings.append(data['Top_Features'].index(feature) + 1)
                else:
                    # Penalty for not in top 10
                    rankings.append(len(data['Top_Features']) + 1)
            feature_rankings[feature] = rankings

        # Convert to DataFrame
        methods = [data['Method'] for data in comparison_data]
        rank_df = pd.DataFrame(feature_rankings, index=methods).T

        # Plot heatmap of rankings
        plt.figure(figsize=(12, 10))
        sns.heatmap(rank_df, annot=True, cmap='viridis_r',
                    cbar_kws={'label': 'Rank (lower is better)'})
        plt.title(f'Feature Importance Comparison - {model_name}\n(Rankings across methods)',
                  fontweight='bold', fontsize=14)
        plt.tight_layout()
        plt.show()

    def overfitting_analysis(self, model, X_train, X_test, y_train, y_test):
        """Analyze potential overfitting"""
        print("PERFORMING OVERFITTING ANALYSIS")
        print("=" * 40)

        # Train and test scores
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)

        print(f"Training Score: {train_score:.4f}")
        print(f"Test Score: {test_score:.4f}")
        print(f"Score Difference: {train_score - test_score:.4f}")

        if train_score - test_score > 0.1:
            print("⚠️  WARNING: Potential overfitting detected!")
        else:
            print("✅ Model generalization appears good")

        # Learning curve simulation
        train_sizes = np.linspace(0.1, 1.0, 10)
        train_scores = []
        test_scores = []

        for size in train_sizes:
            n_samples = int(len(X_train) * size)
            X_subset = X_train[:n_samples]
            y_subset = y_train[:n_samples]

            model.fit(X_subset, y_subset)
            train_scores.append(model.score(X_subset, y_subset))
            test_scores.append(model.score(X_test, y_test))

        # Plot learning curve
        plt.figure(figsize=(10, 6))
        plt.plot(train_sizes, train_scores, 'o-', label='Training Score')
        plt.plot(train_sizes, test_scores, 'o-', label='Test Score')
        plt.xlabel('Training Set Size')
        plt.ylabel('Score')
        plt.title('Learning Curve - Overfitting Analysis', fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

        return {
            'train_score': train_score,
            'test_score': test_score,
            'score_difference': train_score - test_score,
            'learning_curve': (train_sizes, train_scores, test_scores)
        }

    def comprehensive_model_report(self, model, X_train, X_test, y_train, y_test, model_name=""):
        """Generate comprehensive model evaluation report"""
        print(f"COMPREHENSIVE MODEL REPORT - {model_name}")
        print("=" * 60)

        # 1. Basic performance
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(
            model, 'predict_proba') else None

        # 2. Confusion analysis
        confusion_results = self.detailed_confusion_analysis(
            y_test, y_pred, model_name)

        # 3. Overfitting analysis
        overfitting_results = self.overfitting_analysis(
            model, X_train, X_test, y_train, y_test)

        # 4. Feature importance
        importance_results = self.compare_feature_importance_methods(
            model, X_test, y_test, model_name)

        # 5. Cross-validation (if computationally feasible)
        try:
            cv_results, _ = self.time_series_cross_validation(
                model, X_train, y_train, n_splits=3)
        except:
            print("Cross-validation skipped due to computational constraints")
            cv_results = {}

        # Compile final report
        report = {
            'model_name': model_name,
            'confusion_metrics': confusion_results,
            'overfitting_analysis': overfitting_results,
            'feature_importance': importance_results,
            'cross_validation': cv_results,
            'final_test_accuracy': confusion_results['accuracy']
        }

        print(f"\n📊 FINAL REPORT SUMMARY - {model_name}")
        print(f"Test Accuracy: {confusion_results['accuracy']:.4f}")
        print(f"Test F1-Score: {confusion_results['f1']:.4f}")
        print(
            f"Overfitting Score: {overfitting_results['score_difference']:.4f}")

        if cv_results:
            print(
                f"CV Accuracy: {cv_results.get('CV_accuracy_mean', 'N/A'):.4f}")

        return report

# Tutorial: Time-series cross-validation and confusion matrices


def evaluation_tutorial(data, target_col='Target'):
    """Tutorial: Implement comprehensive model evaluation"""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    print("MODEL EVALUATION TUTORIAL")
    print("=" * 40)

    # Prepare data
    X = data.drop(columns=[target_col])
    y = (data[target_col] > 0).astype(int)  # Convert to classification

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, shuffle=False  # No shuffle for time series
    )

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Initialize evaluator
    evaluator = ModelEvaluator()

    # 1. Time-series cross-validation
    print("\n1. TIME SERIES CROSS-VALIDATION")
    cv_results, cv_scores = evaluator.time_series_cross_validation(
        model, X_train, y_train)

    # 2. Detailed confusion analysis
    print("\n2. DETAILED CONFUSION ANALYSIS")
    y_pred = model.predict(X_test)
    confusion_results = evaluator.detailed_confusion_analysis(
        y_test, y_pred, "Random Forest")

    # 3. Feature importance
    print("\n3. FEATURE IMPORTANCE ANALYSIS")
    importance_results = evaluator.compare_feature_importance_methods(
        model, X_test, y_test, "Random Forest")

    return evaluator, model, X_test, y_test

# Challenge: SHAP analysis and feature interpretation


def shap_analysis_challenge(evaluator, model, X_test, y_test, top_n_features=10):
    """Challenge: Perform advanced SHAP analysis"""
    print("SHAP ANALYSIS CHALLENGE")
    print("=" * 40)

    # Get SHAP values
    shap_importance, explainer = evaluator.shap_analysis(
        model, X_test, "Challenge Model")

    # Advanced SHAP plots
    shap_values = explainer.shap_values(X_test)

    if isinstance(shap_values, list) and len(shap_values) == 2:
        # Use positive class for binary classification
        shap_values = shap_values[1]

    # 1. Force plot for single prediction
    print("\nGenerating SHAP Force Plot for first prediction...")
    plt.figure(figsize=(10, 4))
    shap.force_plot(explainer.expected_value[1] if hasattr(explainer.expected_value, '__len__') else explainer.expected_value,
                    shap_values[0, :], X_test.iloc[0, :], show=False, matplotlib=True)
    plt.title('SHAP Force Plot - Individual Prediction', fontweight='bold')
    plt.tight_layout()
    plt.show()

    # 2. Decision plot
    print("Generating SHAP Decision Plot...")
    plt.figure(figsize=(10, 8))
    shap.decision_plot(explainer.expected_value[1] if hasattr(explainer.expected_value, '__len__') else explainer.expected_value,
                       shap_values[:20], X_test.columns, show=False)
    plt.title('SHAP Decision Plot - First 20 Predictions', fontweight='bold')
    plt.tight_layout()
    plt.show()

    # 3. Dependence plots for top features
    top_features = shap_importance.head(top_n_features)['feature'].tolist()

    print(
        f"\nGenerating Dependence Plots for top {top_n_features} features...")
    for i, feature in enumerate(top_features[:4]):  # Plot first 4 top features
        plt.figure(figsize=(10, 6))
        shap.dependence_plot(feature, shap_values, X_test, show=False)
        plt.title(f'SHAP Dependence Plot - {feature}', fontweight='bold')
        plt.tight_layout()
        plt.show()

    # Interpretation insights
    print("\n🔍 SHAP ANALYSIS INSIGHTS:")
    print("1. Force plots show how each feature contributes to individual predictions")
    print("2. Decision plots illustrate the model's decision path")
    print("3. Dependence plots reveal feature relationships and interactions")
    print("4. Summary plots provide global feature importance with local effects")

    return shap_importance, explainer


if __name__ == "__main__":
    # Generate sample data
    def generate_sample_data():
        np.random.seed(42)
        n_samples = 1000
        n_features = 15

        X = np.random.randn(n_samples, n_features)

        # Create meaningful relationships
        true_weights = np.random.randn(n_features)
        true_weights[true_weights < 0] = 0  # Only positive relationships

        y_continuous = X @ true_weights + np.random.randn(n_samples) * 0.5
        y_binary = (y_continuous > 0).astype(int)

        feature_cols = [f'Feature_{i}' for i in range(n_features)]
        data = pd.DataFrame(X, columns=feature_cols)
        data['Target'] = y_binary

        return data

    # Run tutorial
    sample_data = generate_sample_data()
    evaluator, model, X_test, y_test = evaluation_tutorial(sample_data)

    # Run SHAP challenge
    shap_importance, explainer = shap_analysis_challenge(
        evaluator, model, X_test, y_test)

    # Comprehensive report
    print("\n" + "=" * 60)
    print("COMPREHENSIVE EVALUATION COMPLETE")
    print("=" * 60)
