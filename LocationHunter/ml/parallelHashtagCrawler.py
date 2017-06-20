import threading
import time
import hashtagCrawler
from pymongo import MongoClient
class HashtagThread(threading.Thread):
    def __init__(self,threadID,name,location_list):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.location_list = location_list
    def run(self):
        hashtagCrawler.getLocationsHashtags(self.location_list)
        print('Thread-'+self.name+' Finished!!')
def main():
    thread_pool = []
    client = MongoClient('localhost', 27017)
    db = client.locationhunter
    location_table = db.city_locations
    hashtag_helper = db.hashtag_helper
    count = 0
    cache_locations = []
    for city in location_table.find({}):
        locations = city['locations']
        locations = filterLocations(locations,hashtag_helper)
        cache_locations.extend(locations)
        if len(cache_locations) >500:
            thread = HashtagThread(count, "Thread"+city['city_id'],cache_locations)
            thread_pool.append(thread)
            cache_locations = list()
            count += 1
    thread = HashtagThread(count, "Thread" + city['city_id'], cache_locations)
    thread_pool.append(thread)
    count+=1
    print(str(count) + " Threads in total")
    for thread in thread_pool:
        thread.start()
    for thread in thread_pool:
        thread.join()
    print('All Job Finished')

def filterLocations(locations,helper):
    retLocation = []
    for location in locations:
        r = helper.find({'location':location['slug']})
        if r.count() >0:
            if not r[0]['mined']:
                retLocation.append(location)
        else:
            retLocation.append(location)
    return retLocation

if __name__ == '__main__':
    main()