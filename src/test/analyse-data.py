# Updating the ExtendedCryptoData class to include TVL
import json
from typing import Optional, NamedTuple

class ExtendedCryptoDataWithTVL(NamedTuple):
    symbol: str
    tweet_count: int
    user_count: int
    coin_gecko_id: str
    marketcap: float
    fdv: float
    twitter_followers: int
    reddit_subscribers: int
    telegram_channel_user_count: Optional[int]
    ath: float
    tvl: Optional[float]
    score: Optional[float] = None

# Adjusting the calculate_extended_score function to incorporate TVL to FDV ratio
def calculate_score_with_tvl(data: ExtendedCryptoDataWithTVL, weights: dict) -> float:
    fdv_ratio = data.fdv / data.marketcap if data.marketcap else 0
    marketcap_score = 1_000_000_000_000 / data.marketcap if data.marketcap else 0
    user_count_score = data.user_count
    fdv_ratio_score = 1 / fdv_ratio if fdv_ratio else 0
    social_score = data.twitter_followers + (data.reddit_subscribers * 2) + (data.telegram_channel_user_count or 0)
    ath_score = 1 / data.ath if data.ath else 0
    tvl_to_fdv_ratio = data.tvl / data.fdv if data.fdv and data.tvl else 0

    return (marketcap_score * weights['marketcap'] +
            user_count_score * weights['userCount'] +
            fdv_ratio_score * weights['fdvRatio'] +
            social_score * weights['socialScore'] +
            ath_score * weights['athScore'] +
            tvl_to_fdv_ratio * weights['tvlToFdvRatio'])

# Modify the analyze_extended_file function to handle TVL
def calculate_crypto_score_adjusted(entry, weights):
    # Safely get values with default fallbacks to handle missing fields and None values
    marketcap = float(entry.get('Marketcap', 1) if entry.get('Marketcap') else 1)
    fdv = float(entry.get('FDV', 1) if entry.get('FDV') else 1)
    tvl = float(entry.get('tvl', 1) if entry.get('tvl') else 1)
    twitter_followers = int(entry.get('twitter_followers', 0) if entry.get('twitter_followers') else 0)
    telegram_user_count = int(entry.get('telegram_channel_user_count', 0) if entry.get('telegram_channel_user_count') else 0)
    ath_change = float(entry.get('ath_percentage_change', 0) if entry.get('ath_percentage_change') else 0)

    # Calculations as before
    fdv_score = 1 / fdv if fdv > 0 else 0
    fdv_marketcap_ratio = 1 / (fdv / marketcap) if marketcap > 0 and fdv > 0 else 0
    fdv_tvl_ratio = 1 / (fdv / tvl) if tvl > 0 and fdv > 0 else 0
    
    # print(f"Token: {entry['symbol']} Marketcap: {marketcap}, FDV: {fdv}, TVL: {tvl}, Twitter Followers: {twitter_followers}, Telegram User Count: {telegram_user_count}, ATH Change: {ath_change}, FDV Score: {fdv_score}, FDV Marketcap Ratio: {fdv_marketcap_ratio}, FDV TVL Ratio: {fdv_tvl_ratio}")

    score = (
                    # marketcap * weights.get('marketcap', 0) +
             # fdv_score * weights.get('fdv', 0) +
             twitter_followers * weights.get('twitter_followers', 0) +
             telegram_user_count * weights.get('telegram_user_count', 0) +
             ath_change * weights.get('ath_change', 0) +
             fdv_marketcap_ratio * weights.get('fdv_marketcap_ratio', 0) +
             fdv_tvl_ratio * weights.get('fdv_tvl_ratio', 0)) / 7
    return score

weights = {
    'marketcap': 0.8,
    'fdv': 0.2,
    'twitter_followers': 0.3,
    'telegram_user_count': 0.1,
    'fdv_marketcap_ratio': 0.5,
    'fdv_tvl_ratio': 0.3,
    'ath_change': 0.4
}

with open('joined_data.json', 'r') as file:
    crypto_data = json.load(file)
    for entry in crypto_data:
        print(entry['symbol'], entry.get('homepage'), entry.get('description'))
        entry['score'] = calculate_crypto_score_adjusted(entry, weights)

# Re-sort and display the top 5 as before
ranked_crypto_data_with_weights = sorted(crypto_data, key=lambda x: x['score'], reverse=True)

for entry in ranked_crypto_data_with_weights:
    print(f"{entry['symbol']}: {entry['score']}")

# This function is ready to use with a CSV that includes the new structure and fields, including TVL.
