import numpy as np
import heapq
import pickle
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.locationhunter
hashtag_table = db.hashtag2vec
with open('hashtagvecs.pkl', 'rb') as f:
    hashtag_vectors = pickle.load(f)

for tag in hashtag_vectors:
	print(tag)
	#hashtag_table.insert({'hashtag':tag,'vec':vec})
	#print(tag)