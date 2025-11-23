from googleapiclient.discovery import build
import pandas as pd

def fetch_youtube_data(query, api_key, max_results=50):
    """
    Fetch YouTube videos and comments in real-time
    """
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Search for videos
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            type='video',
            maxResults=max_results,
            order='date'
        ).execute()
        
        videos_data = []
        comments_data = []
        
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            
            # Get video statistics
            video_stats = youtube.videos().list(
                part='statistics,snippet',
                id=video_id
            ).execute()
            
            if video_stats['items']:
                stats = video_stats['items'][0]['statistics']
                snippet = video_stats['items'][0]['snippet']
                
                videos_data.append({
                    'video_id': video_id,
                    'title': snippet['title'],
                    'published_at': snippet['publishedAt'],
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0))
                })
                
                # Fetch comments
                try:
                    comments_response = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        maxResults=20
                    ).execute()
                    
                    for comment_item in comments_response.get('items', []):
                        comment = comment_item['snippet']['topLevelComment']['snippet']
                        comments_data.append({
                            'video_id': video_id,
                            'comment': comment['textDisplay'],
                            'like_count': comment['likeCount'],
                            'published_at': comment['publishedAt']
                        })
                except:
                    pass  # Comments disabled
        
        videos_df = pd.DataFrame(videos_data)
        comments_df = pd.DataFrame(comments_data)
        
        # Add sentiment to comments
        if not comments_df.empty:
            comments_df['sentiment'] = comments_df['comment'].apply(analyze_sentiment)
        
        return videos_df, comments_df
    
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")
        return pd.DataFrame(), pd.DataFrame()

def analyze_sentiment(text):
    """Simple sentiment analysis"""
    positive_words = ['love', 'great', 'awesome', 'best', 'delicious']
    negative_words = ['hate', 'bad', 'terrible', 'worst']
    
    text_lower = text.lower()
    pos_count = sum([1 for word in positive_words if word in text_lower])
    neg_count = sum([1 for word in negative_words if word in text_lower])
    
    if pos_count > neg_count:
        return 'Positive'
    elif neg_count > pos_count:
        return 'Negative'
    else:
        return 'Neutral'
