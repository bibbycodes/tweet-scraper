import time
import random
from src.utils import is_thread


def check_none(item):
    return item if item else None


def extract_mentions(user_mentions):
    return [{'twitter_user_id': mention.id, 'username': mention.username} for mention in user_mentions]


def tweet_to_dict(tweet):
    print(tweet.author.id, tweet.author.rest_id)
    return {
        "tweet_id": tweet.id,
        "created_on": tweet.created_on.timestamp(),
        "date": tweet.date.timestamp(),
        "text": tweet.text,
        "twitter_user_id": tweet.author.rest_id,
        "is_retweet": tweet.is_retweet,
        "retweeted_tweet_id": tweet.retweeted_tweet.id if tweet.retweeted_tweet else None,
        "is_quoted": tweet.is_quoted,
        "quoted_tweet_id": tweet.quoted_tweet.id if tweet.quoted_tweet else None,
        "is_reply": tweet.is_reply,
        "is_sensitive": tweet.is_sensitive,
        "reply_counts": tweet.reply_counts,
        "quote_counts": tweet.quote_counts,
        "replied_to_tweet_id": tweet.replied_to.id if tweet.replied_to else None,
        "bookmark_count": tweet.bookmark_count,
        "views": tweet.views,
        "likes": tweet.likes,
        "language": tweet.language,
        "retweet_counts": tweet.retweet_counts,
        "source": tweet.source,
        "audio_space_twitter_id": tweet.audio_space_id,
        "user_mentions": extract_mentions(tweet.user_mentions),
        "urls": tweet.urls,
        "hashtags": tweet.hashtags,
        "symbols": [symbol.text for symbol in tweet.symbols],
        "community_note": tweet.community_note,
        "url": tweet.url,
        "threads": tweet.threads,
        "comments": [comment.id for comment in tweet.comments]
    }

def tweet_to_dict_for_api(tweet_data, user):
    simplified_tweet = {
        "id": tweet_data["tweet_id"],
        "text": tweet_data["text"],
        "created_at": tweet_data["created_on"], 
        "user": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "screen_name": user.screen_name,
            "followers_count": user.followers_count
        },
        "urls": [url for url in tweet_data["urls"]],
        "hashtags": [hashtag['text'] for hashtag in tweet_data["hashtags"]],
        "symbols": tweet_data["symbols"]
    }
    print(simplified_tweet)
    return simplified_tweet


def expand_and_parse_tweets(array_of_tweets):
    all_tweets = []
    
    for tweet in array_of_tweets:
        print(tweet, tweet['author'])
        if is_thread(tweet):
            sleep_duration = random.uniform(0, 3)
            time.sleep(sleep_duration)
            print(f"Sleeping before expanding thread! for {sleep_duration} seconds")
            try:
                tweet.expand()
                for thread_tweet in tweet:
                    parsed = (tweet_to_dict(thread_tweet))
                    if parsed not in all_tweets:
                        all_tweets.append(parsed)
            except Exception as e:
                print(f"Error: {e}")
                continue
        else:
            parsed = (tweet_to_dict(tweet))
            if parsed not in all_tweets:
                all_tweets.append(parsed)
    return sorted(all_tweets, key=lambda x: x['created_on'])



def expand_and_parse_tweets_for_api(array_of_tweets):
    all_tweets_and_users = []
    id_to_tweet_map = {}

    for tweet in array_of_tweets:
        if is_thread(tweet):
            try:
                print('expanding thread')
                print(tweet)
                tweet.expand()
                sleep_duration = random.uniform(0, 3)
                print(f'Sleeping for {sleep_duration} seconds')
                time.sleep(sleep_duration)
                for thread_tweet in tweet:
                    parsed = (tweet_to_dict(thread_tweet))
                    user = thread_tweet.author
                    if parsed['tweet_id'] not in id_to_tweet_map:
                        id_to_tweet_map[parsed['tweet_id']] = parsed
                        all_tweets_and_users.append([parsed, user])
            except Exception as e:
                print(f"Error: {e}")
                continue
        else:
            parsed = (tweet_to_dict(tweet))
            user = tweet.author
            if parsed['tweet_id'] not in id_to_tweet_map:
                id_to_tweet_map[parsed['tweet_id']] = parsed
                all_tweets_and_users.append([parsed, user])
    return [tweet_to_dict_for_api(tweet, user) for tweet, user in all_tweets_and_users]

def user_to_dict(self):
    return {
        'twitter_id': self.id,
        'rest_id': self.rest_id,
        'created_at': self.created_at.timestamp(),
        'date': self.date.timestamp(),
        'description': self.description,
        'bio': self.bio,
        'entities': self.entities,
        'fast_followers_count': self.fast_followers_count,
        'favourites_count': self.favourites_count,
        'followers_count': self.followers_count,
        'friends_count': self.friends_count,
        'listed_count': self.listed_count,
        'location': self.location,
        'media_count': self.media_count,
        'name': self.name,
        'normal_followers_count': self.normal_followers_count,
        'profile_banner_url': self.profile_banner_url,
        'profile_image_url_https': self.profile_image_url_https,
        'protected': self.protected,
        'screen_name': self.screen_name,
        'username': self.username,
        'statuses_count': self.statuses_count,
        'verified': self.verified,
        'pinned_tweets': self.pinned_tweets,
        'community_role': self.community_role
    }

def tweet_to_mention(tweet, pool_id=None, social_channel_id=None):
    import json
    # Assuming tweet.author.followers_count is accessible
    follower_count = getattr(tweet.author, 'followers_count', None)

    # Example placeholder values for pool_id and social_channel_id
    # These should be derived based on your application's logic or provided as function parameters
    pool_id = pool_id
    social_channel_id = social_channel_id if social_channel_id is not None else 1  # Default to an example channel

    return {
        "pool_id": pool_id,
        "social_channel_id": social_channel_id,
        "text": tweet.text,
        "raw_data": json.dumps(tweet.__dict__),  # Dumping the whole tweet object as JSON
        "created_at": tweet.created_on,  # Assuming this is the correct datetime object or converted as needed
        "follower_count": follower_count,
        "symbol": ','.join([symbol.text for symbol in tweet.symbols]) if tweet.symbols else None,
        "urls": [url.expanded_url for url in tweet.urls] if tweet.urls else [],
        "handles": [mention.screen_name for mention in tweet.user_mentions] if tweet.user_mentions else [],
        "token_addresses": [],  # This would need specific logic to fill
    }
