import json
import argparse
import re
from collections import defaultdict
from operator import itemgetter

def get_hashtags_from_caption(caption):
    """Function that gets hashtag (lowercase) list from caption
    Args:
        caption (str): caption string

    Returns:
        list: list of strings, list of hashtags 
    Example:
        caption = "#Python\\n #programming"
        hashtags = get_hashtags_from_caption(caption)
        return ["python", "programming"]
    """
    caption = caption.lower()
    reg = re.findall(r"\#\w+", caption)
    return [s.replace("#", "") for s in reg]

def jaccard_similarity(setA, setB):
    """Function that computes Jaccard Similarity score
    Args:
        setA, setB (set)
    Returns:
        float: Jaccard Similarity score
    """
    return float(len(setA & setB)) / len(setA | setB)

def recommend_user(user_vectors, query, k=10):
    """Function that recommends users based on scores
    scores are computed using Jaccard Similarity of sets of hashtags
    Args:
        user_vectors (dict): dict of (user_id, hashtag set)
        query (tuple): (user_id, hashtag set)
        k (int): number of recommended users (10 by default)
    Returns:
        list: a list of (recommended users, score) ordered by jaccard similarity score
    Example:
        user_vectors = {"1": set(["skyline", "nyc"]), "2": set(["food"])}
        query = ("3", set(["skyline"]))
        k = 1
        recommend_user(user_vectors, query, k) should return ["1", 0.5]
        
    """
    scores = [(user_id, jaccard_similarity(hashtags, query[1])) for user_id, hashtags in user_vectors.items()]
    scores = sorted(scores, key=itemgetter(1), reverse=True)
    return scores[0:min(k, len(scores)-1)]
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recommend trips.')
    parser.add_argument('--data_dir', type=str, default='locations.json',
                        help='Directory for storing input data')
    args = parser.parse_args()
    data_dir = args.data_dir
    
    # load json file that contains posts
    with open(data_dir, 'r') as data_file:
        json_data = json.load(data_file)
    data = json_data
    """
    # extract user_id, hashtags pair
    res = [(x['id'], get_hashtags_from_caption(x['caption'])) for x in data if 'caption' in x]
    # turn list to set
    res = [(user_id, set(hashtags)) for user_id, hashtags in res if hashtags]
    user_vectors = defaultdict(set)
    for user_id, hashtags in res:
        user_vectors[user_id] |= hashtags
    query = ("007", set(["nyc", "skyline"]))
    recommended_user_list = recommend_user(user_vectors, query)
    """
    
    
    