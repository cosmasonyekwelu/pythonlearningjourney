
"""
Day 59: Sentiment Analysis with NLP for Financial Markets
Implementation of advanced NLP pipelines for market sentiment analysis
"""

import torch.nn as nn
from transformers import BertForSequenceClassification, BertTokenizer
from transformers import AutoTokenizer, AutoModel, pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
import re
import warnings
warnings.filterwarnings('ignore')

# NLP Libraries

# Deep Learning for NLP

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


class FinancialTextPreprocessor:
    """Preprocess financial text for sentiment analysis"""

    def __init__(self):
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

        # Financial-specific stop words and terms
        self.financial_stop_words = {
            'company', 'inc', 'corp', 'ltd', 'said', 'says', 'reuters',
            'bloomberg', 'financial', 'market', 'stock', 'share', 'price',
            'quarter', 'year', 'million', 'billion', 'percent'
        }
        self.stop_words.update(self.financial_stop_words)

    def clean_text(self, text):
        """Clean and normalize text"""
        if not isinstance(text, str):
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http\S+', '', text)

        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def tokenize_text(self, text):
        """Tokenize text with financial context"""
        tokens = word_tokenize(text)

        # Remove stop words and short tokens
        tokens = [
            token for token in tokens if token not in self.stop_words and len(token) > 2]

        return tokens

    def stem_tokens(self, tokens):
        """Apply stemming to tokens"""
        return [self.stemmer.stem(token) for token in tokens]

    def lemmatize_tokens(self, tokens):
        """Apply lemmatization to tokens"""
        return [self.lemmatizer.lemmatize(token) for token in tokens]

    def preprocess_pipeline(self, text, method='lemmatize'):
        """Complete text preprocessing pipeline"""
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize_text(cleaned_text)

        if method == 'stem':
            processed_tokens = self.stem_tokens(tokens)
        else:  # lemmatize
            processed_tokens = self.lemmatize_tokens(tokens)

        return ' '.join(processed_tokens)


class SentimentAnalyzer:
    """Multiple sentiment analysis approaches for financial text"""

    def __init__(self):
        self.preprocessor = FinancialTextPreprocessor()
        self.vader_analyzer = SentimentIntensityAnalyzer()

        # Initialize transformer models
        try:
            # Financial BERT model
            self.finbert_tokenizer = AutoTokenizer.from_pretrained(
                "ProsusAI/finbert")
            self.finbert_model = AutoModel.from_pretrained("ProsusAI/finbert")
            self.finbert_sentiment = pipeline("sentiment-analysis",
                                              model="ProsusAI/finbert",
                                              tokenizer=self.finbert_tokenizer)
        except:
            print("FinBERT model not available, using fallback")
            self.finbert_sentiment = None

        # Loughran-McDonald financial sentiment dictionary
        self.lm_positive = self._load_lm_dictionary('positive')
        self.lm_negative = self._load_lm_dictionary('negative')
        self.lm_uncertainty = self._load_lm_dictionary('uncertainty')

    def _load_lm_dictionary(self, category):
        """Load Loughran-McDonald dictionary words"""
        # Simplified version - in practice, load from official dictionary
        dictionaries = {
            'positive': ['profit', 'gain', 'success', 'growth', 'positive', 'strong',
                         'improve', 'increase', 'advantage', 'opportunity'],
            'negative': ['loss', 'decline', 'weak', 'negative', 'challenge', 'risk',
                         'decrease', 'failure', 'problem', 'litigation'],
            'uncertainty': ['uncertain', 'maybe', 'possibly', 'potential', 'could',
                            'might', 'perhaps', 'depending', 'conditional']
        }
        return set(dictionaries.get(category, []))

    def vader_sentiment(self, text):
        """VADER sentiment analysis with financial context"""
        scores = self.vader_analyzer.polarity_scores(text)
        return scores

    def textblob_sentiment(self, text):
        """TextBlob sentiment analysis"""
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }

    def loughran_mcdonald_sentiment(self, text):
        """Loughran-McDonald financial sentiment analysis"""
        processed_text = self.preprocessor.preprocess_pipeline(text)
        tokens = processed_text.split()

        positive_count = sum(
            1 for token in tokens if token in self.lm_positive)
        negative_count = sum(
            1 for token in tokens if token in self.lm_negative)
        uncertainty_count = sum(
            1 for token in tokens if token in self.lm_uncertainty)
        total_relevant = positive_count + negative_count + uncertainty_count

        if total_relevant > 0:
            sentiment_score = (
                positive_count - negative_count) / total_relevant
        else:
            sentiment_score = 0

        return {
            'sentiment_score': sentiment_score,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'uncertainty_words': uncertainty_count
        }

    def finbert_sentiment(self, text):
        """FinBERT sentiment analysis"""
        if self.finbert_sentiment is None:
            return {'label': 'NEUTRAL', 'score': 0.5}

        try:
            result = self.finbert_sentiment(
                text[:512])[0]  # Truncate to model limit
            return result
        except:
            return {'label': 'NEUTRAL', 'score': 0.5}

    def ensemble_sentiment(self, text):
        """Combine multiple sentiment analysis methods"""
        if not text or len(text.strip()) < 10:
            return {'overall_sentiment': 0, 'confidence': 0}

        # Get sentiment from multiple methods
        vader_scores = self.vader_sentiment(text)
        textblob_scores = self.textblob_sentiment(text)
        lm_scores = self.loughran_mcdonald_sentiment(text)
        finbert_result = self.finbert_sentiment(text)

        # Convert all to numerical scores between -1 and 1
        vader_score = vader_scores['compound']
        textblob_score = textblob_scores['polarity']
        lm_score = lm_scores['sentiment_score']

        # Convert FinBERT output to numerical score
        if finbert_result['label'] == 'positive':
            finbert_score = finbert_result['score']
        elif finbert_result['label'] == 'negative':
            finbert_score = -finbert_result['score']
        else:  # neutral
            finbert_score = 0

        # Weighted ensemble (adjust weights based on validation)
        weights = {
            'vader': 0.2,
            'textblob': 0.2,
            'loughran_mcdonald': 0.3,
            'finbert': 0.3
        }

        overall_sentiment = (
            weights['vader'] * vader_score +
            weights['textblob'] * textblob_score +
            weights['loughran_mcdonald'] * lm_score +
            weights['finbert'] * finbert_score
        )

        # Calculate confidence based on agreement
        scores = [vader_score, textblob_score, lm_score, finbert_score]
        positive_scores = sum(1 for s in scores if s > 0.1)
        negative_scores = sum(1 for s in scores if s < -0.1)

        confidence = max(positive_scores, negative_scores) / len(scores)

        return {
            'overall_sentiment': overall_sentiment,
            'confidence': confidence,
            'vader_score': vader_score,
            'textblob_score': textblob_score,
            'lm_score': lm_score,
            'finbert_score': finbert_score
        }


class MarketSentimentAnalyzer:
    """Main class for market sentiment analysis"""

    def __init__(self, symbol='AAPL'):
        self.symbol = symbol
        self.sentiment_analyzer = SentimentAnalyzer()

    def generate_sample_news(self):
        """Generate sample financial news for demonstration"""
        sample_news = [
            {
                'headline': f"{self.symbol} reports strong quarterly earnings with 20% revenue growth",
                'date': datetime.now() - timedelta(days=1),
                'source': 'financial_news'
            },
            {
                'headline': f"Analysts downgrade {self.symbol} due to concerns about future growth prospects",
                'date': datetime.now() - timedelta(days=2),
                'source': 'analyst_report'
            },
            {
                'headline': f"{self.symbol} announces new product line and expansion into emerging markets",
                'date': datetime.now() - timedelta(days=3),
                'source': 'company_news'
            },
            {
                'headline': f"Market volatility affects {self.symbol} shares amid economic uncertainty",
                'date': datetime.now() - timedelta(days=4),
                'source': 'market_news'
            },
            {
                'headline': f"{self.symbol} faces regulatory challenges in key international markets",
                'date': datetime.now() - timedelta(days=5),
                'source': 'regulatory_news'
            }
        ]
        return pd.DataFrame(sample_news)

    def analyze_news_sentiment(self, news_df):
        """Analyze sentiment for a dataframe of news articles"""
        sentiments = []

        for _, row in news_df.iterrows():
            sentiment_result = self.sentiment_analyzer.ensemble_sentiment(
                row['headline'])

            sentiment_data = {
                'date': row['date'],
                'headline': row['headline'],
                'source': row['source'],
                'overall_sentiment': sentiment_result['overall_sentiment'],
                'confidence': sentiment_result['confidence'],
                'vader_score': sentiment_result['vader_score'],
                'textblob_score': sentiment_result['textblob_score'],
                'lm_score': sentiment_result['lm_score'],
                'finbert_score': sentiment_result['finbert_score']
            }
            sentiments.append(sentiment_data)

        return pd.DataFrame(sentiments)

    def fetch_market_data(self, period='1mo'):
        """Fetch market data for correlation analysis"""
        stock_data = yf.download(self.symbol, period=period)
        stock_data['returns'] = stock_data['Close'].pct_change()
        stock_data['price'] = stock_data['Close']
        return stock_data

    def correlate_sentiment_returns(self, sentiment_df, market_data):
        """Correlate sentiment scores with market returns"""
        # Merge sentiment and market data
        merged_data = []

        for date in sentiment_df['date']:
            market_row = market_data[market_data.index.date == date.date()]
            if not market_row.empty:
                sentiment_row = sentiment_df[sentiment_df['date']
                                             == date].iloc[0]

                merged_point = {
                    'date': date,
                    'sentiment': sentiment_row['overall_sentiment'],
                    'returns': market_row['returns'].iloc[0],
                    'price_change': (market_row['Close'].iloc[0] - market_row['Open'].iloc[0]) / market_row['Open'].iloc[0]
                }
                merged_data.append(merged_point)

        correlation_df = pd.DataFrame(merged_data)

        if len(correlation_df) > 1:
            sentiment_return_corr = correlation_df['sentiment'].corr(
                correlation_df['returns'])
            sentiment_price_corr = correlation_df['sentiment'].corr(
                correlation_df['price_change'])
        else:
            sentiment_return_corr = 0
            sentiment_price_corr = 0

        return correlation_df, sentiment_return_corr, sentiment_price_corr

    def create_sentiment_timeseries(self, sentiment_df):
        """Create daily sentiment time series"""
        sentiment_df['date_only'] = sentiment_df['date'].dt.date
        daily_sentiment = sentiment_df.groupby('date_only').agg({
            'overall_sentiment': 'mean',
            'confidence': 'mean',
            'vader_score': 'mean',
            'textblob_score': 'mean',
            'lm_score': 'mean',
            'finbert_score': 'mean'
        }).reset_index()

        return daily_sentiment

    def plot_sentiment_analysis(self, sentiment_df, correlation_df, market_data):
        """Plot comprehensive sentiment analysis results"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Plot 1: Sentiment scores over time
        daily_sentiment = self.create_sentiment_timeseries(sentiment_df)
        axes[0, 0].plot(daily_sentiment['date_only'], daily_sentiment['overall_sentiment'],
                        marker='o', linewidth=2, label='Overall Sentiment')
        axes[0, 0].set_title('Daily Sentiment Scores')
        axes[0, 0].set_ylabel('Sentiment Score')
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        # Plot 2: Component sentiment scores
        axes[0, 1].plot(daily_sentiment['date_only'], daily_sentiment['vader_score'],
                        label='VADER', alpha=0.7)
        axes[0, 1].plot(daily_sentiment['date_only'], daily_sentiment['textblob_score'],
                        label='TextBlob', alpha=0.7)
        axes[0, 1].plot(daily_sentiment['date_only'], daily_sentiment['lm_score'],
                        label='Loughran-McDonald', alpha=0.7)
        axes[0, 1].plot(daily_sentiment['date_only'], daily_sentiment['finbert_score'],
                        label='FinBERT', alpha=0.7)
        axes[0, 1].set_title('Component Sentiment Scores')
        axes[0, 1].set_ylabel('Sentiment Score')
        axes[0, 1].legend()
        axes[0, 1].grid(True)

        # Plot 3: Sentiment vs Returns scatter
        if len(correlation_df) > 0:
            axes[1, 0].scatter(correlation_df['sentiment'],
                               correlation_df['returns'], alpha=0.6)
            axes[1, 0].set_xlabel('Sentiment Score')
            axes[1, 0].set_ylabel('Daily Returns')
            axes[1, 0].set_title(
                f'Sentiment vs Returns (Corr: {correlation_df["sentiment"].corr(correlation_df["returns"]):.3f})')
            axes[1, 0].grid(True)

            # Add trend line
            z = np.polyfit(correlation_df['sentiment'],
                           correlation_df['returns'], 1)
            p = np.poly1d(z)
            axes[1, 0].plot(correlation_df['sentiment'], p(
                correlation_df['sentiment']), "r--")

        # Plot 4: Price and sentiment overlay
        if not market_data.empty and len(daily_sentiment) > 0:
            ax2 = axes[1, 1].twinx()

            # Price line
            color = 'tab:blue'
            axes[1, 1].plot(market_data.index,
                            market_data['price'], color=color, label='Price')
            axes[1, 1].set_xlabel('Date')
            axes[1, 1].set_ylabel('Price', color=color)
            axes[1, 1].tick_params(axis='y', labelcolor=color)

            # Sentiment line
            color = 'tab:red'
            ax2.plot(daily_sentiment['date_only'], daily_sentiment['overall_sentiment'],
                     color=color, label='Sentiment', linewidth=2)
            ax2.set_ylabel('Sentiment', color=color)
            ax2.tick_params(axis='y', labelcolor=color)

            axes[1, 1].set_title('Price and Sentiment Overlay')
            axes[1, 1].grid(True)

        plt.tight_layout()
        plt.savefig('sentiment_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

    def run_complete_analysis(self):
        """Run complete sentiment analysis pipeline"""
        print("Starting Financial Sentiment Analysis...")
        print("=" * 50)

        # Generate sample news data
        print("1. Generating sample financial news...")
        news_df = self.generate_sample_news()

        # Analyze sentiment
        print("2. Analyzing sentiment using multiple methods...")
        sentiment_df = self.analyze_news_sentiment(news_df)

        # Fetch market data
        print("3. Fetching market data for correlation analysis...")
        market_data = self.fetch_market_data()

        # Correlate sentiment with returns
        print("4. Correlating sentiment with market returns...")
        correlation_df, return_corr, price_corr = self.correlate_sentiment_returns(
            sentiment_df, market_data)

        # Display results
        print("\n" + "=" * 50)
        print("SENTIMENT ANALYSIS RESULTS")
        print("=" * 50)
        print(f"Symbol: {self.symbol}")
        print(f"News Articles Analyzed: {len(sentiment_df)}")
        print(f"Sentiment-Return Correlation: {return_corr:.3f}")
        print(f"Sentiment-Price Change Correlation: {price_corr:.3f}")

        print("\nDetailed Sentiment Scores:")
        for _, row in sentiment_df.iterrows():
            print(f"\nDate: {row['date'].strftime('%Y-%m-%d')}")
            print(f"Headline: {row['headline']}")
            print(
                f"Overall Sentiment: {row['overall_sentiment']:.3f} (Confidence: {row['confidence']:.3f})")

        # Plot results
        print("\n5. Generating visualizations...")
        self.plot_sentiment_analysis(sentiment_df, correlation_df, market_data)

        return sentiment_df, correlation_df, market_data


def main():
    """Main function to run sentiment analysis"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Financial Sentiment Analysis')
    parser.add_argument('--symbol', type=str, default='AAPL',
                        help='Stock symbol for analysis')
    parser.add_argument('--real_time', action='store_true',
                        help='Enable real-time analysis')

    args = parser.parse_args()

    # Initialize and run analysis
    analyzer = MarketSentimentAnalyzer(symbol=args.symbol)
    sentiment_df, correlation_df, market_data = analyzer.run_complete_analysis()

    print("\nAnalysis completed successfully!")
    print(f"Results saved to: sentiment_analysis.png")


if __name__ == "__main__":
    main()
