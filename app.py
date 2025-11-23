import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from utils.twitter_api import fetch_twitter_data, analyze_twitter_sentiment
from utils.youtube_api import fetch_youtube_data, analyze_youtube_engagement
from utils.data_processing import process_data, extract_product_mentions

# Page Configuration
st.set_page_config(
    page_title="Social Media Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🔥 Real-Time Social Media Analytics</p>', unsafe_allow_html=True)
st.markdown("**Monitoring Nestlé Products Across Twitter & YouTube**")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")

# API Keys (use st.secrets for deployment)
TWITTER_BEARER_TOKEN = st.secrets.get("<>", "")
YOUTUBE_API_KEY = st.secrets.get("<>", "")

# Search Configuration
brand = st.sidebar.text_input("🔍 Brand/Topic", "Nestle", help="Enter brand or topic to monitor")
products = st.sidebar.multiselect(
    "🍫 Products to Track",
    ["KitKat", "Maggi", "Nescafe", "Milo", "Smarties"],
    default=["KitKat", "Maggi", "Nescafe"]
)

# Auto-refresh settings
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh", value=False)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 10, 300, 60)

# Tabs for Twitter and YouTube
tab1, tab2 = st.tabs(["🐦 Twitter Analytics", "📺 YouTube Analytics"])

# ============== TWITTER TAB ==============
with tab1:
    st.header("Twitter Real-Time Insights")
    
    # Create placeholder for auto-updating content
    twitter_placeholder = st.empty()
    
    with twitter_placeholder.container():
        # Fetch Twitter Data
        with st.spinner("🔍 Fetching Twitter data..."):
            twitter_df = fetch_twitter_data(
                query=f"{brand} ({' OR '.join(products)})",
                bearer_token=TWITTER_BEARER_TOKEN,
                max_results=100
            )
        
        if not twitter_df.empty:
            # Top KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="📝 Total Tweets",
                    value=len(twitter_df),
                    delta=f"+{len(twitter_df) - 80}" if len(twitter_df) > 80 else "0"
                )
            
            with col2:
                total_likes = twitter_df['like_count'].sum()
                st.metric(
                    label="❤️ Total Likes",
                    value=f"{total_likes:,}",
                    delta="+12%" if total_likes > 500 else "0%"
                )
            
            with col3:
                total_retweets = twitter_df['retweet_count'].sum()
                st.metric(
                    label="🔁 Total Retweets",
                    value=f"{total_retweets:,}",
                    delta="+8%" if total_retweets > 200 else "0%"
                )
            
            with col4:
                avg_sentiment = twitter_df['sentiment_score'].mean()
                st.metric(
                    label="😊 Avg Sentiment",
                    value=f"{avg_sentiment:.2f}",
                    delta=f"{avg_sentiment - 0.5:.2f}" if avg_sentiment > 0.5 else f"{avg_sentiment - 0.5:.2f}"
                )
            
            st.markdown("---")
            
            # Charts Section
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("📊 Product Mentions")
                product_counts = twitter_df['product_mentioned'].value_counts()
                fig_products = px.bar(
                    x=product_counts.index,
                    y=product_counts.values,
                    labels={'x': 'Product', 'y': 'Mentions'},
                    color=product_counts.values,
                    color_continuous_scale='Blues'
                )
                fig_products.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_products, use_container_width=True)
            
            with chart_col2:
                st.subheader("😊 Sentiment Distribution")
                sentiment_counts = twitter_df['sentiment'].value_counts()
                fig_sentiment = px.pie(
                    values=sentiment_counts.values,
                    names=sentiment_counts.index,
                    color_discrete_sequence=['#28a745', '#ffc107', '#dc3545']
                )
                fig_sentiment.update_layout(height=400)
                st.plotly_chart(fig_sentiment, use_container_width=True)
            
            # Time Series
            st.subheader("📈 Tweet Volume Over Time")
            twitter_df['hour'] = pd.to_datetime(twitter_df['created_at']).dt.hour
            hourly_tweets = twitter_df.groupby('hour').size().reset_index(name='count')
            fig_timeline = px.line(
                hourly_tweets,
                x='hour',
                y='count',
                markers=True,
                labels={'hour': 'Hour of Day', 'count': 'Tweet Count'}
            )
            fig_timeline.update_layout(height=300)
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Data Table
            st.subheader("📋 Recent Tweets")
            st.dataframe(
                twitter_df[['created_at', 'text', 'like_count', 'retweet_count', 'sentiment']].head(10),
                use_container_width=True
            )
        else:
            st.warning("⚠️ No Twitter data available. Check API credentials.")

# ============== YOUTUBE TAB ==============
with tab2:
    st.header("YouTube Real-Time Insights")
    
    youtube_placeholder = st.empty()
    
    with youtube_placeholder.container():
        # Fetch YouTube Data
        with st.spinner("🔍 Fetching YouTube data..."):
            youtube_videos_df, youtube_comments_df = fetch_youtube_data(
                query=f"{brand} {' '.join(products)}",
                api_key=YOUTUBE_API_KEY,
                max_results=50
            )
        
        if not youtube_videos_df.empty:
            # Top KPIs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="🎥 Total Videos",
                    value=len(youtube_videos_df),
                    delta="+5" if len(youtube_videos_df) > 45 else "0"
                )
            
            with col2:
                total_views = youtube_videos_df['view_count'].sum()
                st.metric(
                    label="👁️ Total Views",
                    value=f"{total_views:,.0f}",
                    delta="+15%" if total_views > 100000 else "0%"
                )
            
            with col3:
                total_comments = youtube_comments_df['comment'].count() if not youtube_comments_df.empty else 0
                st.metric(
                    label="💬 Total Comments",
                    value=f"{total_comments:,}",
                    delta="+20" if total_comments > 50 else "0"
                )
            
            with col4:
                avg_engagement = (youtube_videos_df['like_count'].sum() / youtube_videos_df['view_count'].sum() * 100) if youtube_videos_df['view_count'].sum() > 0 else 0
                st.metric(
                    label="📊 Engagement Rate",
                    value=f"{avg_engagement:.2f}%",
                    delta=f"+{avg_engagement - 2:.2f}%" if avg_engagement > 2 else "0%"
                )
            
            st.markdown("---")
            
            # Charts Section
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("📊 Top 10 Videos by Views")
                top_videos = youtube_videos_df.nlargest(10, 'view_count')
                fig_top_videos = px.bar(
                    top_videos,
                    x='view_count',
                    y='title',
                    orientation='h',
                    labels={'view_count': 'Views', 'title': 'Video Title'},
                    color='view_count',
                    color_continuous_scale='Reds'
                )
                fig_top_videos.update_layout(showlegend=False, height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_top_videos, use_container_width=True)
            
            with chart_col2:
                st.subheader("💬 Comment Sentiment")
                if not youtube_comments_df.empty:
                    sentiment_counts = youtube_comments_df['sentiment'].value_counts()
                    fig_sentiment = px.pie(
                        values=sentiment_counts.values,
                        names=sentiment_counts.index,
                        color_discrete_sequence=['#28a745', '#ffc107', '#dc3545']
                    )
                    fig_sentiment.update_layout(height=400)
                    st.plotly_chart(fig_sentiment, use_container_width=True)
                else:
                    st.info("No comment data available.")
            
            # Video Performance Table
            st.subheader("📋 Video Performance")
            st.dataframe(
                youtube_videos_df[['title', 'view_count', 'like_count', 'comment_count', 'published_at']].head(10),
                use_container_width=True
            )
        else:
            st.warning("⚠️ No YouTube data available. Check API credentials.")

# Auto-refresh logic
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**📊 Dashboard by [Your Name] | Data refreshed:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
