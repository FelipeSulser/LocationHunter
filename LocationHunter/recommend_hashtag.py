import pprint
import operator
import pandas as pd
from collections import defaultdict
from pymongo import MongoClient


def naive_recommend_hashtags(location='shanghai', k=10):
    """Function that recommends a list of k hashtags based on popularity score given location
    popularity score = total like_count/occurrence
    Args:
        location (str): location string
        k (int): number of recommended hashtags, 10 by default
    Returns:
        list: sorted list (hashtag, score, count) in descending order of popularity
    Example:
        location = 'rennes'
        recommended_hashtags = naive_recommend_hashtags(location)
    """
    client = MongoClient()
    # change db and collection name if needed
    client = MongoClient('localhost', 27017)
    db = client['locationhunter']
    collection = db['cached_location']
    query = collection.find({'name':location}, {'cachedposts':1, '_id':0})
    res = [item for item in query]
    if not res:
        return []
    res = res[0]
    hashtag_list_with_like_count = [(post['hashtags'], post['like_count']) for post in res['cachedposts'] if post['hashtags']]
    hashtag_like_count = [[hashtag.lower(), like_count, like_count] for hashtag_list, like_count in hashtag_list_with_like_count for hashtag in hashtag_list]
    df = pd.DataFrame(hashtag_like_count, columns=['hashtag', 'score', 'like_count'])
    grouped = df.groupby(by='hashtag', sort=False, as_index=False)
    agg_df = grouped['score'].mean()
    col_like_count = grouped['like_count'].sum()
    agg_df['like_count'] = col_like_count['like_count']
    res = agg_df.sort_values(by=['score'], ascending=0)
    return res[0:k].values.tolist()

if __name__ == '__main__':
    location = 'shanghai'
    recommended_hashtags = naive_recommend_hashtags(location, 30)

