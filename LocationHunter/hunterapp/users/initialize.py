import numpy as np
import pickle
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.locationhunter
user_table = db.user
k = 50
for user in user_table.find({}):
    print(user['user_id'])
    z_ta = np.random.rand(k)
    with open(user['user_id'] + '_z.pkl', 'wb') as f:
        pickle.dump(z_ta, f, pickle.HIGHEST_PROTOCOL)