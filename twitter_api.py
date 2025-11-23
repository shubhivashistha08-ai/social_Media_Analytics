import tweepy
import pandas as pd
from datetime import datetime, timedelta

def fetch_twitter_data(query, bearer_token, max_results=100):
    """
    Fetch real-time Twitter data using Twitter API v2
    """
    try:
        client = tweepy.Client(bearer_token=bearer_token)
        
        # Search recent tweets
        tweets = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=['created_at', 'public_metrics', 'lang'],
            expansions=['author_id']
        )
        
        # Process tweets
        data = []
        if tweets.data:
            for tweet in tweets.data:
                data.append({
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'like_count': tweet.public_metrics['like_count'],
                    'retweet_count': tweet.public_metrics['retweet_count'],
                    'reply_count': tweet.public_metrics['reply_count'],
                    'lang': tweet.lang
                })
        
        df = pd.DataFrame(data)
        
        # Add sentiment analysis (simple keyword-based)
        if not df.empty:
            df['sentiment'] = df['text'].apply(analyze_sentiment)
            df['sentiment_score'] = df['sentiment'].map({'Positive': 1, 'Neutral': 0.5, 'Negative': 0})
            df['product_mentioned'] = df['text'].apply(extract_product)
        
        return df
    
    except Exception as e:
        print(f"Error fetching Twitter data: {e}")
        return pd.DataFrame()

def analyze_sentiment(text):
    """Simple sentiment analysis"""
    positive_words = ['love', 'great', 'awesome', 'best', 'delicious', 'yummy', 'excellent']
    negative_words = ['hate', 'bad', 'terrible', 'worst', 'disgusting', 'awful']
    
    text_lower = text.lower()
    pos_count = sum([1 for word in positive_words if word in text_lower])
    neg_count = sum([1 for word in negative_words if word in text_lower])
    
    if pos_count > neg_count:
        return 'Positive'
    elif neg_count > pos_count:
        return 'Negative'
    else:
        return 'Neutral'

def extract_product(text):
    """Extract product mentions"""
    products = ['kitkat', 'maggi', 'nescafe', 'milo', 'smarties']
    text_lower = text.lower()
    
    for product in products:
        if product in text_lower:
            return product.capitalize()
    return 'Other'
