# Day 63: Weekly Project – Integrated AI Trading Agent

**Date:** November 23, 2025

## Learning Objective
To build a "Super-Agent" that integrates Deep Learning for price prediction, NLP for sentiment analysis, and Reinforcement Learning for trade execution.

## Concepts Covered
- **Modular Integration**: Combining disparate AI components into a cohesive decision-making pipeline.
- **Ensemble Decision Making**: Using signals from both technical indicators and qualitative news sentiment.
- **Attention-based LSTM**: Using deep sequences to predict short-term market reversals.
- **Backtesting Rigger**: Evaluating the complete system across different historical periods.
- **Unified Data Pipeline**: Building a robust loader that handles market data, simulated sentiment, and correlation features.

## Code Explanation
The `day_sixtythree.py` script is the orchestrator for the `AITradingAgent`:
- **`DataPipeline`**: Prepares a 3D feature tensor containing technical indicators, sentiment scores, and cross-asset returns.
- **`DeepLearningPredictor`**: An LSTM model with a custom Attention layer trained to predict the next day's expected return.
- **`SentimentAnalyzer`**: Leverages the FinBERT transformer model to provide context from headlines.
- **`execute_trades()`**: Applies a confidence-weighted sizing rule to determine the exact number of shares to trade.

## How to Run
1. Install requirements: `pip install torch transformers stable-baselines3 yfinance scikit-learn`
2. Run the agent:
```bash
python week_09/daysixtythree/day_sixtythree.py --symbols AAPL MSFT GOOGL AMZN TSLA
```
3. Check `ai_trading_agent_report.json` for a detailed performance breakdown.

## Reflection
The future of trading isn't just one algorithm; it's an ecosystem of agents working together. This project demonstrates how NLP can provide the "mood" of the market, while Deep Learning provides the "trend," and RL manages the "timing" and "risk."
