# Day 58: LSTM for Time Series Prediction

**Date:** November 18, 2025

## Learning Objective
To implement Long Short-Term Memory (LSTM) networks, a type of Recurrent Neural Network (RNN) designed to capture long-term dependencies in sequential market data.

## Concepts Covered
- **LSTM Architecture**: Understanding Gates (Input, Forget, Output) and Cell State.
- **Bidirectional LSTMs**: Processing the sequence in both forward and backward directions to capture more context.
- **Attention Mechanisms**: Implementing a layer that allows the model to focus on the most important historical time steps.
- **Sequence Engineering**: Preparing 3D tensors (Batch, Time, Features) for RNN training.
- **Regression Modeling**: Predicting the exact percentage change in price rather than just direction.

## Code Explanation
The `day_fiftyeight.py` script implements the `LSTMForecaster`:
- **`FinancialLSTM`**: A sophisticated model supporting multiple layers, bidirectionality, and an optional Attention layer.
- **`AttentionLayer`**: Manually implements the alignment mechanism to weight different parts of the lookback window.
- **`fetch_data()`**: Integrates the `ta` library to create a rich 20+ feature input vector including MACD, ADX, and Bollinger Bands.
- **Visualization**: Generates a comparison plot of Actual vs. Predicted returns.

## How to Run
1. Install requirements: `pip install torch pandas numpy yfinance ta matplotlib`
2. Run the LSTM trainer:
```bash
python week_09/dayfiftyeight/day_fiftyeight.py --symbol MSFT --attention --epochs 30
```

## Reflection
LSTMs are specifically designed for data where the order matters. By adding an Attention mechanism, we help the model identify which past events (like a price spike 10 days ago) are most relevant to tomorrow's prediction.
