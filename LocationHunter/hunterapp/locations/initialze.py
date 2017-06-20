import numpy as np
import heapq
import pickle
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.locationhunter
location_table = db.location_hashtags
id_table = db.locations
with open('locvecs.pkl', 'rb') as f:
    location_vectors = pickle.load(f)
def getLocationVector(name):
    if name in location_vectors:
        return location_vectors[name]
    else:
        return np.random.rand(50)
def getLocationId(name):
    for id in id_table.find({'slug':name}):
        return id['id']
if __name__ == '__main__':
    # Initial the Global Variable
    k = 50 # USER
    d = 50 # ITEM
    A0 = np.identity(k)
    b0 = np.zeros(k)
    with open('A0_v.pkl', 'wb') as f:
        pickle.dump(np.linalg.inv(A0), f, pickle.HIGHEST_PROTOCOL)
    with open('b0.pkl', 'wb') as f:
        pickle.dump(b0, f, pickle.HIGHEST_PROTOCOL)
    # Initial Item Variable
    Aa = np.identity(d)
    Ba = np.zeros([d,k])
    ba = np.zeros(d)
    count = 0
    for location in location_table.find({}):
        vectors = {}
        x_ta = getLocationVector(location['location'])
        vectors['A_v'] = np.linalg.inv(Aa)
        vectors['B'] = Ba
        vectors['bias'] = ba
        vectors['x'] = x_ta
        with open(getLocationId(location['location']) + '_vs.pkl', 'wb') as f:
            pickle.dump(vectors, f, pickle.HIGHEST_PROTOCOL)
        count += 1
        print(location['location'])
    print(count)




