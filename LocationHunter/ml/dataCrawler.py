import requests
import json
from pymongo import MongoClient
def cralwerPopularLocationInCitiy(city_id,city_name):
    print('find all the locations')
    headers = {'authority': 'www.instagram.com',
               'method': 'POST',
               'path': '/explore/locations/'+city_id+'/',
               'scheme': 'https',
               'accept': 'application/json',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'zh-CN,zh;q=0.8',
               'content-length': '6',
               'content-type': 'application/x-www-form-urlencoded',
               'cookie': 'mid=WJ731gALAAGLwbTIM8mHiLTpUytS; fbm_124024574287414=base_domain=.instagram.com; sessionid=IGSC64e1c7d5417a5c69dcec4e7632af45b54d27fc217ee4a653a8eb4040552f1248%3AcI7BOggzAeQXWFfwGu5RLMDWvxYOSRwg%3A%7B%22_auth_user_id%22%3A4712872839%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_token_ver%22%3A2%2C%22_token%22%3A%224712872839%3Afq1AvzhwsTTNVegRYbO9JfKEB9exFZdW%3A68e7bf64d72df79171956cc7913f8ee0a60aad8f3c44faff3bb42f4b507cb8e8%22%2C%22_platform%22%3A4%2C%22last_refreshed%22%3A1493147954.4088466167%2C%22asns%22%3A%7B%22time%22%3A1493147951%2C%2262.12.154.122%22%3A15623%7D%7D; s_network=""; ig_vw=1366; ig_pr=1; fbsr_124024574287414=PS7UF-r5kPxDuAdkqch1BPVrYCFR2mdGnUGxMosvpVs.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUNaa2lhUEt2eFJvTkgtQkNkanZ5X29jdm5LZE5Ga1Bzem1PR0lXYnhucEdNTTg2aUdLMEpNdEl2Z3Nma0N2OGNtdmpkZUVXNFdYdDdkY0xqS2UySTBQdEFxTS1IbWxaN3VQek1oV0xXM01rSlBXZ3d5R1ZDd0p2S2c5V3ZOSTRwLTVDa2o3dFlwbVdRMEpWVlhYbjBoZzVzNl9ZaVVoTDQ5Sk4yNjAwTldHam9zMW9zNnVoVy1laTdsQ0VySkx2UF9rLV84YUxEX1FyN01UUlJXVGEyQzRQMURsQktxOC1BOWVDa1ZaRjRsbzZ1c3NwZV9kRHJwZTFQUWhiRWNqVS1PckVuR1FGRkp6ZUlTbjZHUFA3VS1Rcl8xRFVyX2J4N1VnV25UeUhXcV9KcXI1a3NDY2pwbzlPM1Z2eU0zTzBNMVN1UWYydWU5dW5XbHE1MFdTN1VHRSIsImlzc3VlZF9hdCI6MTQ5MzE0ODE5MSwidXNlcl9pZCI6IjEwMDAwNzc2MTIyMTMyNSJ9; rur=PRN; csrftoken=zuaPzduXtCDwzWYwHaMyTk2Infz32Kdq; ds_user_id=4712872839',
               'origin': 'https://www.instagram.com',
               'referer': 'https://www.instagram.com/explore/locations/'+city_id+'/'+city_name+'-switzerland/',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
               'x-csrftoken': 'zuaPzduXtCDwzWYwHaMyTk2Infz32Kdq',
               'x-instagram-ajax': '1',
               'x-requested-with': 'XMLHttpRequest',
    }
    data = {'page':1}
    r = requests.post('https://www.instagram.com/explore/locations/'+city_id+'/', data=data, headers=headers)
    if not is_json(r.text):
        return None
    locations = json.loads(r.text)['location_list']
    return locations
def getCityList():
    client = MongoClient('localhost', 27017)
    db = client.locationhunter
    city_table = db.cities
    cities = city_table.find({'country_id':'CH'},{'cities':1})[0]['cities']
    return cities
def saveCityLocations(city_id,locations):
    client = MongoClient('localhost', 27017)
    db = client.locationhunter
    location_table = db.city_locations
    location_table.insert({'city_id':city_id,'locations':locations})
    #location_table.save()
def main():
    '''
    cities = getCityList()
    count = 0
    for city in cities:
        print(city['name'])
        locations = cralwerPopularLocationInCitiy(city['id'],city['name'])
        if locations is not None:
            saveCityLocations(city['id'],locations)
            count+=1
            print('Success')
    print(str(count)+'finished')
    '''


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True
if __name__ == '__main__':
    main()