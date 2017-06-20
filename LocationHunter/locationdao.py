import heapq
import json
import pickle
import threading
import time

import numpy as np
import requests
from pymongo import MongoClient

import lock

client = MongoClient('localhost', 27017)
db = client.locationhunter
location_table = db.locations
country_table = db.cities
# Shared Attributes
with open('./hunterapp/locations/A0_v.pkl', 'rb') as f:
    A0_v = pickle.load(f)
with open('./hunterapp/locations/b0.pkl', 'rb') as f:
    b0 = pickle.load(f)
b0 = b0.reshape(len(b0), 1)
A0 = np.linalg.inv(A0_v)
location_cache = {}
user_cache = {}
beta = np.dot(A0_v, b0)
# Lock
public_var_lock = lock.RWLock()
location_locks = dict()


class UpdatingThread(threading.Thread):
    def __init__(self, threadID, name, cache):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.cache = cache
        self.last_update = dict()
        self.running = True

    def run(self):
        while (self.running):
            for key, value in self.cache.items():
                if value['updated']:
                    with open('./hunterapp/locations/' + key + '_vs.pkl', 'wb') as f:
                        value['updated'] = False
                        location_locks[key].acquire_read()
                        pickle.dump(value, f, pickle.HIGHEST_PROTOCOL)
                        location_locks[key].release()
            public_var_lock.acquire_read()
            with open('./hunterapp/locations/A0_v.pkl', 'wb') as f:
                pickle.dump(A0_v, f, pickle.HIGHEST_PROTOCOL)
            with open('./hunterapp/locations/b0.pkl', 'wb') as f:
                pickle.dump(b0, f, pickle.HIGHEST_PROTOCOL)
            public_var_lock.release()
            time.sleep(1)

    def stop(self):
        self.running = False

# Updating Thread
updating_thread = UpdatingThread(1, 'updating', location_cache)
updating_thread.start()


# TODO:LOCK AND CHECK
# It is only read
def getScore(id, z):
    global A0
    global A0_v
    global b0
    global location_cache
    global beta
    global user_cache
    if id in location_cache:
        vs = location_cache[id]
    else:
        with open('./hunterapp/locations/' + id + '_vs.pkl', 'rb') as f:
            vs = pickle.load(f)



    Aa_v = vs['A_v']
    Ba = vs['B']
    ba = vs['bias'].reshape(len(vs['bias']), 1)
    xa = vs['x'].reshape(len(vs['x']), 1)
    location_cache[id] = vs
    location_cache[id]['updated'] = False
    location_locks[id] = lock.RWLock()
    location_locks[id].acquire_read()
    public_var_lock.acquire_read()
    cta = np.dot(Aa_v
                 , (ba - np.dot(Ba, beta)))
    s = z.T.dot(A0_v).dot(z)
    s -= 2 * z.T.dot(A0_v).dot(Ba.T).dot(Aa_v).dot(xa)
    s += float((xa.T.dot(Aa_v).dot(xa)))
    s += float(xa.T.dot(Aa_v).dot(Ba).dot(A0_v).dot(Ba.T).dot(Aa_v).dot(xa))
    p = float(z.T.dot(beta) + xa.T.dot(cta) + 0.1 * (s ** 2))
    public_var_lock.release()
    location_locks[id].release()

    return p


def recLocations(city_name, user_id):
    global user_cache
    rec_locs = []
    if user_id in user_cache:
        user_vector = user_cache[user_id]
    else:
        with open('./hunterapp/users/' + user_id + '_z.pkl', 'rb') as f:
            user_vector = pickle.load(f)
            user_cache[user_id] = user_vector
    top_scores = []
    for location in location_table.find({'belong_city': city_name}):
        score = getScore(location['id'], user_vector)
        # print(score)
        heapq.heappush(top_scores, (score, location))
        if len(top_scores) > 8:
            heapq.heappop(top_scores)
    while len(top_scores) > 0:
        score, loc = heapq.heappop(top_scores)
        rec = {}
        rec['id'] = loc['id']
        rec['slug'] = loc['slug']
        rec['name'] = loc['name']
        rec['belong_city'] = loc['belong_city']
        rec['pic'] = loc['image_url']
        rec['lat'] = loc['lat']
        rec['lon'] = loc['lon']
        rec_locs.append(rec)
        print(loc['id'])
    return rec_locs[::-1]


def allocateFeedBacks(accept_ids, decline_ids, user_id):
    global A0
    global A0_v
    global b0
    global location_cache
    global beta
    global user_cache

    if user_id in user_cache:
        z = user_cache[user_id]
    else:
        with open('./hunterapp/users/' + user_id + '_z.pkl', 'rb') as f:
            z = pickle.load(f)
            user_cache[user_id] = z
    for id in accept_ids:
        if id in location_cache:
            # variable preparation
            location_locks[id].acquire_write()
            Ba = location_cache[id]['B']
            Aa_v = location_cache[id]['A_v']
            xa = location_cache[id]['x']
            ba = location_cache[id]['bias']
            Aa = np.linalg.inv(Aa_v)
            # Updating
            public_var_lock.acquire_write()
            A0 += Ba.T.dot(np.linalg.inv(Aa)).dot(Ba)
            b0 += (Ba.T.dot(np.linalg.inv(Aa)).dot(ba)).reshape(len(b0), 1)
            Aa += xa.reshape(len(xa), 1).dot(xa.reshape(len(xa), 1).T)
            Ba += xa.reshape(len(xa), 1).dot(z.reshape(len(z), 1).T)
            ba += 1 * xa
            A0 += z.dot(z.T) - Ba.T.dot(np.linalg.inv(Aa)).dot(Ba)
            b0 += (1 * z - Ba.T.dot(np.linalg.inv(Aa)).dot(ba)).reshape(len(b0), 1)
            # Refresh Back
            location_cache[id]['A_v'] = np.linalg.inv(Aa)
            A0_v = np.linalg.inv(A0)
            beta = np.dot(A0_v, b0)
            location_cache[id]['updated'] = True
            public_var_lock.release()
            location_locks[id].release()
    for id in decline_ids:
        if id in location_cache:
            # variable preparation
            Ba = location_cache[id]['B']
            Aa_v = location_cache[id]['A_v']
            xa = location_cache[id]['x']
            ba = location_cache[id]['bias']
            Aa = np.linalg.inv(Aa_v)
            # Updating
            public_var_lock.acquire_write()
            A0 += Ba.T.dot(np.linalg.inv(Aa)).dot(Ba)
            b0 += Ba.T.dot(np.linalg.inv(Aa)).dot(ba).reshape(len(b0), 1)
            Aa += xa.reshape(len(xa), 1).dot(xa.reshape(len(xa), 1).T)
            Ba += xa.reshape(len(xa), 1).dot(z.reshape(len(z), 1).T)
            ba += 1 * xa
            A0 += z.dot(z.T) - Ba.T.dot(np.linalg.inv(Aa)).dot(Ba)
            b0 += (1 * z - Ba.T.dot(np.linalg.inv(Aa)).dot(ba)).reshape(len(b0), 1)
            # Refresh Back
            location_cache[id]['A_v'] = np.linalg.inv(Aa)
            A0_v = np.linalg.inv(A0)
            beta = np.dot(A0_v, b0)
            location_cache[id]['updated'] = True
            public_var_lock.release()


# TODO:GET GOOGLE
def getPicture(location_id, location_slug):
    headers = {'authority': 'www.instagram.com',
               'method': 'POST',
               'path': '/query/',
               'scheme': 'https',
               'accept': 'application/json',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'zh-CN,zh;q=0.8',
               'content-length': '548',
               'content-type': 'application/x-www-form-urlencoded',
               'cookie': 'mid=WJ731gALAAGLwbTIM8mHiLTpUytS; fbm_124024574287414=base_domain=.instagram.com; sessionid=IGSC7aeabca3024edab97e822c64e9360448a73f3df3363ed4649d43cbada067e1bf%3A7u8Ra1TPhQFriRrfw1W5gD3Si46mp1x5%3A%7B%22_auth_user_id%22%3A4712872839%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_token_ver%22%3A2%2C%22_token%22%3A%224712872839%3AQyfFtpP92mAFSLAG2EMD1nc0LsKlbuEW%3Af0efcb029151b7232c856597eb156458edd72f7e9a670e9a641613b9cf70b6a0%22%2C%22_platform%22%3A4%2C%22last_refreshed%22%3A1493562945.5056936741%2C%22asns%22%3A%7B%22time%22%3A1493562945%2C%2262.12.154.122%22%3A15623%7D%7D; fbsr_124024574287414=IHU5mGgvuySywaCf6Sq_exIU3JIQxJvGlfbfVPVhqcA.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUE4R2V3b3pBRXlCTFZFdTROaXhEMjJtSVRyS21pbEV2TXdpRmpGSTVZU19xR1p0VDgzV0hiRUFpb2lOWktWSmY4bUduZjRZT1RZTDFtSldueUE1c0J2aEgwWTh0MThfSVlfQzd5LXhyT1dfZWR2YWh5anpEMEdsV3dnbHJISW80eHNzaFNZTmk4YnBNamwxVklUdVFrelE2QTNPR2ZmS3NwUW5FTGNJMTJEOS0tLW5hUDBPdVJjRkxFdmJhbTN4bnVGVzl6OUxfT1dsTXl3dExhN1pUcXRYOFVMbkkxZDJvYnQ4Z3VERGhRVEMyYVFKYUNSOGRxaUE4OE1BdEZkV0lMbHpjNmotbUFzNTc5U1pYTnZyVXI0bThiNnJ1RTlUVnRaWEZKbU5ZZnR0TWZ6d0NCR3R3bkladjJyYW5QbFV4UVhEb1hJWEFIREIweTRiUG93c0R4VyIsImlzc3VlZF9hdCI6MTQ5MzU2MzM2OSwidXNlcl9pZCI6IjEwMDAwNzc2MTIyMTMyNSJ9; rur=PRN; s_network=""; csrftoken=yql1uNf3PfdI5UfG9FlRxVar2glNaTRX; ds_user_id=4712872839; ig_vw=1366; ig_pr=1',
               'origin': 'https://www.instagram.com',
               'referer': 'https://www.instagram.com/explore/locations/' + location_id + '/' + location_slug + '/',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.8',
               'x-csrftoken': 'yql1uNf3PfdI5UfG9FlRxVar2glNaTRX',
               'x-instagram-ajax': '1',
               'x-requested-with': 'XMLHttpRequest',
               }
    data = {
        'q': 'ig_location(' + location_id + ') { media.after(1437690628975827805, 3) {count,nodes {__typename,caption,code,comments {count},comments_disabled,date,dimensions {height,width},display_src,id,likes {count},owner {id},thumbnail_src}}}',
        'ref': 'locations::show', 'query_id': ''}
    r = requests.post('https://www.instagram.com/query/', data=data, headers=headers)
    node = json.loads(r.text)['media']['nodes']
    if len(node) == 0:
        return None
    pic = json.loads(r.text)['media']['nodes'][0]['thumbnail_src']
    return pic


def getAllCities(country_id):
    country = country_table.find({'country_id': country_id}, {'cities': 1})[0]
    city_list = []
    if len(country) == 0:
        return None
    for city in country['cities']:
        city_list.append(city['name'])
    return city_list


if __name__ == '__main__':
    # print(getPicture('16121080','chapel-bridge'))

    user = np.random.rand(50)
    recLocations('lucerne', '4712872839')
    allocateFeedBacks(['229112883', '524251'], ['301542'], '4712872839')

    updating_thread.stop()
    updating_thread.join()
    # mylocak = lock.RWLock()
    print('Finish')
