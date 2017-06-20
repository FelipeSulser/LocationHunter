import requests
from pymongo import MongoClient
import json
import numpy as np
import time
import numpy as np
import math
import re
import schedule
from unidecode import unidecode
from django.db import connection
from django.core.mail import EmailMessage
from hunterapp import *  #Relative import
from mongoengine import *

def getHashtags():
  client = MongoClient('localhost', 27017)
  db = client.locationhunter
  users = db.user
  for user in users.find():
    #data_user = User(user_id=user['user_id'])
    print(user['username'])
    print(user['user_id'])
    hashtag_list = user['user_specific_hashtags']
    header={'Host': 'i.instagram', 
              'X-IG-Capabilities': '36o=',
              'Cookie': 'csrftoken=dFhXHEBvUth6toAeIaVnNm8hkWaKCq3F; ds_user_id=3568831550; rur=ATN; s_network=""; is_starred_enabled=yes; igfl=sulserfelipe; sessionid=IGSC2bc67a82fc3bebf28a29f47b29a78ac8f5a9a5911838a6d047763c29f238e99c%3AOqjQBIkzMwbetApOh4h3XrYKcu92JYiQ%3A%7B%22_platform%22%3A0%2C%22_auth_user_id%22%3A3568831550%2C%22_auth_user_hash%22%3A%22%22%2C%22last_refreshed%22%3A1491483616.7723619938%2C%22asns%22%3A%7B%222001%3A67c%3A10ec%3A52c7%3A8000%3A%3A4c%22%3A559%2C%22time%22%3A1491483616%7D%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_token_ver%22%3A2%2C%22_token%22%3A%223568831550%3AO30E02IT3VldCXFyyACYViKOziR2sIe9%3Af65e5502d56eb58b0694738aabb028c4a4d368f12b1e795dc4a7f387a0dd4ed7%22%7D;ds_user=sulserfelipe; mid=V5E1YgAAAAEMbcRIM5TyLqE031df',
              'Connection':'keep-alive',
              'Accept':'*/*',
              'User-Agent':'Instagram 10.14.0 (iPhone8,1; iOS 10_2_1; en_CH; en-CH; scale=2.00; gamut=normal; 750x1334) AppleWebKit/420+',
              'Accept-Language':'en-CH;q=1, de-CH;q=0.9',
              'Accept-Encoding':'gzip, deflate',
              'X-IG-Connection-Type':'WiFi'}
    to_add = set()
    for ht_elem in hashtag_list:
      ress = requests.get("https://i.instagram.com/api/v1/tags/"+ht_elem+"/related?related_types=[\"hashtag\"]",header)
      to_add_list = ress.json()['related']
      for elem in to_add_list:
        to_add.add(elem['name'])
    set_ht = set(hashtag_list)
    set_ht = set_ht.union(to_add)
    hashtag_list = list(set_ht)
    #clean unicodes
    myre = re.compile(u'['
    u'\U0001F300-\U0001F64F'
    u'\U0001F680-\U0001F6FF'
    u'\u2600-\u26FF\u2700-\u27BF]+', 
    re.UNICODE)
    hashtag_list = [unidecode(myre.sub('',x)) for x in hashtag_list]
    mydict = {
      'user_specific_hashtags' : hashtag_list
    }
    print(hashtag_list)
    #mycollection.update({'_id':mongo_id}, {"$set": post}, upsert=False)
    users.update({'user_id': user['user_id']},{"$set":mydict},upsert=False)
   



def crawlByUserId(user_id,user_name):
    # for followers
    ret_info = {}
    headers = {'authority': 'www.instagram.com',
                   'method':'POST',
                   'path':'/query/',
                   'scheme':'https',
                   'accept':'application/json',
                   'accept-encoding':'gzip, deflate, br',
                   'accept-language':'zh-CN,zh;q=0.8',
                   'content-length':'415',
                   'content-type':'application/x-www-form-urlencoded',
                   'cookie':'mid=WJ731gALAAGLwbTIM8mHiLTpUytS; fbm_124024574287414=base_domain=.instagram.com; sessionid=IGSCd0584fd621440fba86026573ed438cf4fa105d82f695055ebde8f821c599b689%3AmrI4tz9Qa2iKvNTZOTFM2N4iuMMkV2kl%3A%7B%22last_refreshed%22%3A1490635194.9347462654%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_platform%22%3A4%2C%22_auth_user_hash%22%3A%22%22%2C%22_token%22%3A%224712929548%3AqIS0JnSkiBcU8tvdOKSVY7xZcOu5skiv%3A15206b1d23d095157e90299a14ec1c76fcc9ad632bdbe370053cdab7baa4251b%22%2C%22_token_ver%22%3A2%2C%22_auth_user_id%22%3A4712929548%2C%22asns%22%3A%7B%222001%3A67c%3A10ec%3A52cb%3A8000%3A%3A6c%22%3A559%2C%22time%22%3A1490635198%7D%7D; s_network=""; ig_vw=1366; ig_pr=1; fbsr_124024574287414=b1REa0uhXtC18mh2xp4TJqpc93sY5p5HD3CsucT2O2o.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUFlYjJnVzdQSEU1M3ZVOUN1aWEtS1E0ODdtTVJYSVJvTjVtQUZ6TE1aZTFBXzJKLVQ3UXZWNkhsVFhIT1drbmJ2MDcwc2R6WklaSnU3emFXSTY5SEN3dHNWUXVON0x2eWdfWmQzSE45Y3BUanJ5WlR1V1M3ejJvQWJIOVpIWXhxZ0JlTXF1REhKQTB1UjlhUUF0eXBicXVzX0lRZ1EyWm81eHVTcGtQR0M3ay1RbWtvV2ZES3RrX0YwR0xDb2JZVENteHRaS19xcFphV0lXWV95S1lYal9haGNKdnloUTlSNi1laEg2b2hBcEVlX0Z6WFU0UWVMX3E2MXJ1d3ZJLUVadDNvcm53VHdpM1dSVWVhOHMybTlhUDE2R0tNUk5SQlROaWZ4YlBaWEpvaGZqQ1Bidk9Wdm91aVlMQ2tDODh3OWVlZl9Gb1ZxV2RtT2hYVkFPQUo4azRiQTF4RERuc1NPRE5VMElGVVVYNHciLCJpc3N1ZWRfYXQiOjE0OTA2OTYwNjksInVzZXJfaWQiOiIxMDAwMDc3NjEyMjEzMjUifQ; ds_user_id='+user_id+'; csrftoken=1QKwNoiW49WFV9slsHZ1sGhX91SW3sTY',
                    'origin':'https://www.instagram.com',
                   'referer': 'https://www.instagram.com/'+user_name+'/',
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.8',
                   'x-csrftoken': '1QKwNoiW49WFV9slsHZ1sGhX91SW3sTY',
                   'x-instagram-ajax': '1',
                   'x-requested-with': 'XMLHttpRequest',
                   }
    data ={'q':'ig_user('+user_id+') {followed_by.first(20) {count,page_info {end_cursor,has_next_page},nodes {id,is_verified,followed_by_viewer,requested_by_viewer,full_name,profile_pic_url,username}}}','ref':'relationships::follow_list','query_id':'17845270936146575'}
    r = requests.post('https://www.instagram.com/query/', data=data,headers=headers)
    #print(r.text)
    ret_info['followers'] = (json.loads(r.text))['followed_by']['count']
    # for follwoing
    headers['content-length'] = '411'
    headers['cookie']= 'mid=WJ731gALAAGLwbTIM8mHiLTpUytS; fbm_124024574287414=base_domain=.instagram.com; sessionid=IGSCd0584fd621440fba86026573ed438cf4fa105d82f695055ebde8f821c599b689%3AmrI4tz9Qa2iKvNTZOTFM2N4iuMMkV2kl%3A%7B%22last_refreshed%22%3A1490635194.9347462654%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_platform%22%3A4%2C%22_auth_user_hash%22%3A%22%22%2C%22_token%22%3A%224712929548%3AqIS0JnSkiBcU8tvdOKSVY7xZcOu5skiv%3A15206b1d23d095157e90299a14ec1c76fcc9ad632bdbe370053cdab7baa4251b%22%2C%22_token_ver%22%3A2%2C%22_auth_user_id%22%3A4712929548%2C%22asns%22%3A%7B%222001%3A67c%3A10ec%3A52cb%3A8000%3A%3A6c%22%3A559%2C%22time%22%3A1490635198%7D%7D; s_network=""; ig_vw=1366; ig_pr=1; fbsr_124024574287414=M2EKK8g-opWmwg9btkZ4_67Twa5gmrcUdq8gbhJ6ZCA.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUURHMjNHQnVCb0JORjN6TDhTUloxT0pMc1dGZEdiYTZaVG1jZjJ5clFNMUk5VUZNWktHMTd3dWhjQ2czekoxamlTeFFrZEFLUGw0cVVjUU9teFlvdy1vb3hTTm5CUk96bGFORUp5MUYzbjRYVHBYN2Q0SHhCVzAwbHN4V2kyOTNHVFlXZWxDZF9mTS12aHBDcTJMY0hOeDN5SDJDVXRwblNGeVFtYlhySkhqNmtLRXMxcUswd1JjRWEwM1UtcHE0aUR1MVFmc21yVGdwejVabkRqM21ZYkFpa0RqQ2h3ejRDNTJnTU5HcGN1bnloN2NjVTRMOERjak16aEhtMXc3YzJJcC1nb3dsTUZ5QVgweE5ZR1hBNG9MNzVCZmF5el9ab19ELUdhRk0zOW95TEVBSWJnZHdzaGp1SzFCQzE2U3lxU3ZJVzFrYkxvT1pNbXAzV2JFNlcwWCIsImlzc3VlZF9hdCI6MTQ5MDcxNDg3NywidXNlcl9pZCI6IjEwMDAwNzc2MTIyMTMyNSJ9; csrftoken=1QKwNoiW49WFV9slsHZ1sGhX91SW3sTY; ds_user_id='+user_id
    data['query_id'] = '17867281162062470'
    data['q'] = 'ig_user('+user_id+') {follows.first(20) {count,page_info {end_cursor,has_next_page},nodes {id,is_verified,followed_by_viewer,requested_by_viewer,full_name,profile_pic_url,username}}}'
    r = requests.post('https://www.instagram.com/query/', data=data,headers=headers)

    ret_info['follows'] = (json.loads(r.text))['follows']['count']
    # for media
    headers['content-length'] = '559'
    headers['cookie'] = 'mid=WJ731gALAAGLwbTIM8mHiLTpUytS; fbm_124024574287414=base_domain=.instagram.com; sessionid=IGSCd0584fd621440fba86026573ed438cf4fa105d82f695055ebde8f821c599b689%3AmrI4tz9Qa2iKvNTZOTFM2N4iuMMkV2kl%3A%7B%22last_refreshed%22%3A1490635194.9347462654%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_platform%22%3A4%2C%22_auth_user_hash%22%3A%22%22%2C%22_token%22%3A%224712929548%3AqIS0JnSkiBcU8tvdOKSVY7xZcOu5skiv%3A15206b1d23d095157e90299a14ec1c76fcc9ad632bdbe370053cdab7baa4251b%22%2C%22_token_ver%22%3A2%2C%22_auth_user_id%22%3A4712929548%2C%22asns%22%3A%7B%222001%3A67c%3A10ec%3A52cb%3A8000%3A%3A6c%22%3A559%2C%22time%22%3A1490635198%7D%7D; fbsr_124024574287414=KM67bepPQpcYrGuEfIbaDgkxAc9yOoAqzZphnG9Fsoc.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUFTdFJrV2xuWTEzOHUwR2ZaemUzV2k5VGd4ZmRLcVhGTi1CNlQxVXBJWWdUckVfbjR0bGgwLWxSTm4tZzA3X2RSTVJ6ZVBhcUF2TnBha1ozNXc1Ny1xUjlKOEJtUGh3YlVVeW5jZmpnVUo1RFNZdGVBenIxN1M5bExrRHNTMUI3MUZ0c1RKb1lkLXphY21VaHRTdDNxQVFDWEdpSG5EdThlbzllYTh2MGZPSmsxZFNwZFZUdkRGRlhyXzIyQ2gzSjdqaS1TT3RlbHZDc2lLYWp0Y2t4UlB3bFhuVlk2NmJZcmFJMktYS29lcXFSa0luTXl4TURGazdCY1VQX0ludURVZkY3eGxSOGp0ZGUxLVRRdjNmei16eGp1MmgybzE5NE9yNEczejdVTWJ2WHNaNTNOMmtLeWVuWUNTaWpEVTlnTThMWWFNVnBDU3BVZlRscjIxYmQ4ayIsImlzc3VlZF9hdCI6MTQ5MDcxNTgxNCwidXNlcl9pZCI6IjEwMDAwNzc2MTIyMTMyNSJ9; ig_vw=1366; ig_pr=1; ds_user_id='+user_id+'; csrftoken=1QKwNoiW49WFV9slsHZ1sGhX91SW3sTY; s_network=""'
    data['q']= 'ig_user('+user_id+') { media.after(1466231012161195245, 12) {count,nodes {__typename,caption,code,comments {count},comments_disabled,date,dimensions {height,width},display_src,id,is_video,likes {count},owner {id},thumbnail_src,video_views},page_info}}'
    data['ref'] = 'users::show'
    data['query_id'] = '17849115430193904'
    r = requests.post('https://www.instagram.com/query/', data=data,headers=headers)

    ret_info['medias'] = (json.loads(r.text))['media']['count']


    # for the following list
    following_list = []
    total = ret_info['follows']
    each = 30
    base_url = 'https://www.instagram.com/graphql/query/?query_id=17874545323001329&'
    base_url += 'id='+user_id+'&first='+str(each)
    batch = {}
    headers = {
        'cookie': 'mid=WJ731gALAAGLwbTIM8mHiLTpUytS; fbm_124024574287414=base_domain=.instagram.com; sessionid=IGSC315e0da14594818b10ec29eb55ccb35a63c4187eea8665b638252380f4e15f17%3AsNOPnIe8IV8h9Ejku940wkjCkeWg5ZXr%3A%7B%22_auth_user_id%22%3A4712929548%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_token_ver%22%3A2%2C%22_token%22%3A%224712929548%3A9usbEgjU5Zou2ApMcXNYLQHNnmhDljzQ%3A70bbd9652a59aac7671bd796767a90c9223c7af6c7a9f13f151ea878d2a6c28a%22%2C%22_platform%22%3A4%2C%22last_refreshed%22%3A1492168111.4486522675%2C%22asns%22%3A%7B%22time%22%3A1492168472%2C%2262.12.154.122%22%3A15623%7D%7D; ds_user_id=4712929548; rur=FRC; csrftoken=osd38s1hxr8YRWlP1801zHyhicFoeM2X'
    }
    for i in range(math.ceil(total/each)):
        if i == 0:
            r = requests.get(base_url,headers=headers)

        else:
            r = requests.get(base_url+"&after="
                             +batch['data']['user']['edge_follow']['page_info']['end_cursor']
                             ,headers=headers)

        batch = json.loads(r.text)
        following_list.extend(np.asarray(batch['data']['user']['edge_follow']['edges']))

    ret_info['following_list'] =  following_list
    return ret_info


#Read last two entries from the array and calculate the trend
def getTrendLine(arr, title):
	l = len(arr)
	strn = ""		
	if(l >= 2):
		strn = title+"\n"
		diff = int(100.0*(arr[l-1]['value']-arr[l-2]['value'])/arr[l-2]['value'])
		sgn = ""		
		if(diff > 0 ):
			sgn = "+"
		strn = strn + str(arr[l-1]['value']) +  " (" +sgn + str(diff) + " %) \n"  
	return strn



def send_email_digests():   
	connect('locationhunter')      
	for user in User.objects.all():
		if(user.email_digest == "on"):
			print("Preparing: " + user.username + "'s email ...")
			text = 'Hi %s, here\'s your daily digest \n\n' % user.username
			loggedUser = User.objects(username=user.username)
			toEmail = loggedUser[0]['email']					
			
			text += getTrendLine(loggedUser[0]['followers_trend'],'Followers')
			text += getTrendLine(loggedUser[0]['followed_people_trend'],'Followed People')
			text += getTrendLine(loggedUser[0]['media_trend'],'Media')
			text += getTrendLine(loggedUser[0]['likes_trend'],'Likes')

			print(text)
			subject = 'Your Daily Digest'
			msg = EmailMessage(subject, text, 'Location Hunter', [toEmail])
			msg.send()




def start():
    client = MongoClient('localhost', 27017)
    db = client.locationhunter
    users = db.user
    print("Executing background job now...")

    for user in users.find():
        print(user['username'])
        print(user['user_id'])
        trend = crawlByUserId(user['user_id'],user['username'])
        #print (trend)
        print(len(trend['following_list']))
        stamp = int(time.time())
        users.update(
            {"user_id":user['user_id']},
            {"$push":
                 {"media_trend":{"date":stamp,"value":trend['medias']}},
            }
        )
        users.update(
            {"user_id": user['user_id']},
            {"$push":
                {"followers_trend": {"date": stamp, "value": trend['followers']}},
             }
        )
        users.update(
            {"user_id": user['user_id']},
            {"$push":
                 {"followed_people_trend": {"date": stamp, "value": trend['follows']}},
             }
        )
        for index in range(len(trend['following_list'])):
            trend['following_list'][index] = trend['following_list'][index]['node']
        users.update(
            {"user_id": user['user_id']},
            {"$set":
                 {"followed_people_list":trend['following_list']} ,
             }
        )
        #current_user = User.objects(user_id=user['user_id'])[0]
        #current_user.followed_people_list = trend['following_list']
        #current_user.save()
    # get the new data and then add back
    
schedule.every().day.at("23:50").do(start)



#DONT run this, or my account will get banned --felipe
#schedule.every().wednesday.at("23:15").do(getHashtags)
while True:
    schedule.run_pending()
    time.sleep(60)


#send_email_digests()


