# Day 57: Neural Networks Fundamentals for Finance

**Date:** November 17, 2025

## Learning Objective
To understand the fundamentals of Deep Learning and implement a Multi-Layer Perceptron (MLP) for predicting market direction using PyTorch.

## Concepts Covered
- **PyTorch Basics**: Tensors, Autograd, and Module classes.
- **MLP Architecture**: Designing input, hidden, and output layers with Batch Normalization and Dropout.
- **Activation Functions**: Comparing ReLU, Leaky ReLU, Tanh, and Sigmoid.
- **Loss Functions & Optimizers**: Using Binary Cross Entropy with Logits and the Adam optimizer.
- **Data Engineering**: Creating sliding windows (sequences) from historical price data.

## Code Explanation
The `day_fiftyseven.py` script implements a `FinancialNeuralNetwork`:
- **`FinancialMLP`**: A custom PyTorch model that can be configured with a variable number of layers and units.
- **`FinancialDataset`**: A custom PyTorch Dataset class for handling time-series sequences.
- **`train_model()`**: Implements the training loop with validation checks and learning rate scheduling.
- **Evaluation**: Calculates test accuracy to judge the model's ability to predict "Up" vs "Down" days.

## How to Run
1. Install requirements: `pip install torch pandas numpy yfinance scikit-learn`
2. Run the neural network training:
```bash
python week_09/dayfiftyseven/day_fiftyseven.py --symbol AAPL --epochs 50
```

## Reflection
While traditional ML models work well on tabular data, Neural Networks provide the flexibility to learn complex, non-linear patterns. However, they are sensitive to hyperparameters and require careful regularization (like Dropout) to avoid overfitting on noisy financial data.
