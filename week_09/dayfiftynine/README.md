# Day 59: Sentiment Analysis with NLP

**Date:** November 19, 2025

## Learning Objective
To utilize Natural Language Processing (NLP) to quantify market sentiment from financial news and headlines, and correlate it with asset performance.

## Concepts Covered
- **Text Preprocessing**: Tokenization, lemmatization, and removing financial-specific stop words.
- **VADER Sentiment**: A rule-based tool specifically tuned for social media and financial context.
- **FinBERT**: Leveraging pre-trained Transformer models (BERT) specialized for the financial domain.
- **Lexicon-based Analysis**: Using the Loughran-McDonald dictionary to identify "uncertainty" and "litigation" words.
- **Ensemble Sentiment**: Combining multiple NLP signals into a single "Confidence" score.

## Code Explanation
The `day_fiftynine.py` script implements a `MarketSentimentAnalyzer`:
- **`FinancialTextPreprocessor`**: Uses `nltk` to clean raw headlines.
- **`SentimentAnalyzer`**: Integrates Hugging Face `transformers` and `textblob` for multi-layered analysis.
- **`correlate_sentiment_returns()`**: Merges NLP scores with actual `yfinance` price data to calculate Pearson correlation coefficients.
- **Visualization**: Plots a price line chart overlaid with a sentiment heat map.

## How to Run
1. Install dependencies: `pip install transformers torch vaderSentiment textblob nltk yfinance matplotlib`
2. Run the analysis:
```bash
python week_09/dayfiftynine/day_fiftynine.py --symbol TSLA
```

## Reflection
Market sentiment often leads price action. By converting qualitative news into quantitative scores, we can gain an informational edge over traders who only look at historical charts.
