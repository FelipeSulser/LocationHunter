import time
import crawl_post_by_location
import re
from pymongo import MongoClient
# TODO:To design a parallel solution
media_count_per_request = '10'
max_number_of_posts_to_fetch = 20
last_timestamp = 1490711
def getLocationsHashtags(location_list):
    client = MongoClient('localhost', 27017)
    db = client.locationhunter
    hashtag_table = db.location_hashtags
    hashtag_helper = db.hashtag_helper
    for location in location_list:
        print(location['slug'])
        location_id = location['id']
        location_slug = location['slug']
        posts = crawl_post_by_location. \
            crawl_post_by_loc(location_id, location_slug, media_count_per_request,
                              max_number_of_posts_to_fetch, last_timestamp)
        try_times = 0
        # for recover
        while len(posts)<0:
            time.sleep(60)
            try_times+=1
            print('Try more')
            posts = crawl_post_by_location. \
                crawl_post_by_loc(location_id, location_slug, media_count_per_request,
                                  max_number_of_posts_to_fetch, last_timestamp)
            if try_times >5:
                print('expired')
                exit(-1)
        # for tf-idf representation
        tag_map = dict()
        # for hashtag embedings
        tag_order_list = list()
        for post in posts:
            if 'caption' in post:
                cap = post['caption']
                # TODO:the Regular Expression can be more precise
                tags = re.findall(r'#([a-zA-Z0-9_-]+)', cap)
                if len(tags) > 0:
                    tag_order_list.append(tags)
                for tag in tags:
                    if tag in tag_map:
                        tag_map[tag] += 1
                    else:
                        tag_map[tag] = 1
        if(len(posts)>20):
            saveRawRepresentation(hashtag_table,hashtag_helper,location_slug,tag_map,tag_order_list)
            print('Saved!')



def saveRawRepresentation(table,helper,slug,tag_map,tag_order_list):
    table.insert({'location':slug,'tag_map':tag_map,'tag_order_list':tag_order_list})
    helper.insert({'location':slug,'mined':True})

def main():
    client = MongoClient('localhost', 27017)
    db = client.locationhunter
    location_table = db.city_locations
    for city in location_table.find({}).limit(1):
        getLocationsHashtags(city['locations'])


if __name__ == '__main__':
    main()

