# Create your views here.
import datetime
import json
import re
import time

import requests
import userInstgramProxy
import userStatHelper
import userdao
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from hunterapp.models import *
from mongoengine import *
from pymongo import MongoClient
from recommend_hashtag import naive_recommend_hashtags
from recommend_user import recommend_user
from unidecode import unidecode
from InstagramAPI import InstagramAPI
from .crawler import crawl_post_by_location
from .crawler import crawl_user
import locationdao
from multiprocessing.dummy import Pool as ThreadPool 
from twilio.rest import Client
# https://api.instagram.com/oauth/authorize/?client_id=06c1a4fb726246a783c8c2b17e792685&redirect_uri=http://127.0.0.1:8000/locationhunter/homepage&response_type=code
def verification(request):
  #template = loader.get_template('hunterapp/login.html')
  context = {}
  return HttpResponse("google-site-verification: google486a122b04c93dd1.html")

login_map = {}
def welcome(request):
  template = loader.get_template('hunterapp/login.html')
  context = {}
  return HttpResponse(template.render(context,request))
def direct(request):
    template = loader.get_template('hunterapp/direct_page.html')
    context = {}  
    return HttpResponse(template.render(context, request))
# GET
def mongodbtest(request):
    return HttpResponse('User already exists')

def logout_view(request):
  logout(request)
  template = loader.get_template('hunterapp/direct_page.html')
  context = {}
  return HttpResponse(template.render(context,request))

def adminLogging(request):
    login = {}
    if(('user_id' in request.COOKIES) and (request.session.has_key(request.COOKIES['user_id']))):
        login = request.session[request.COOKIES['user_id']]
        print(login) 
        #get aggregated data
        totalNumFofAccepted = 0
        totalNumFofDismissed = 0
        totalNumLocationsAccepted = 0
        totalNumLocationsDismissed = 0
        fofaccepted_doc = {}
        fofdismissed_doc = {}
        locationsaccepted_doc={}
        locationsdismissed_doc = {}
        connect('locationhunter')
        for user in User.objects:
          print(user.numFofAccepted)
          totalNumFofAccepted += user.numFofAccepted
          totalNumFofDismissed += user.numFofDismissed
          totalNumLocationsAccepted += user.numLocationsAccepted
          totalNumLocationsDismissed += user.numLocationsDismissed
          fofaccepted_doc[user.username] = user.numFofAccepted
          fofdismissed_doc[user.username] = user.numFofDismissed
          locationsaccepted_doc[user.username] = user.numLocationsAccepted
          locationsdismissed_doc[user.username] = user.numLocationsDismissed

        template = loader.get_template('hunterapp/admin_logging.html')
        context = {'numfofaccepted':totalNumFofAccepted,
        'numfofdismissed': totalNumFofDismissed,
        'numlocationsaccepted': totalNumLocationsAccepted,
        'numlocationsdismissed': totalNumLocationsDismissed,
        'dicfofaccepted':fofaccepted_doc,
        'dicfofdismissed':fofdismissed_doc,
        'diclocationsaccepted':locationsaccepted_doc,
        'diclocationsdismissed':locationsdismissed_doc}

        return HttpResponse(template.render(context,request))
    else:
      return HttpResponse('Please log in')
def homepage(request):
    login = {}
    if(('user_id' in request.COOKIES) and (request.session.has_key(request.COOKIES['user_id']))):
        login = request.session[request.COOKIES['user_id']]
        print(login)

    else:
        # get authorization
        data={'client_id': '06c1a4fb726246a783c8c2b17e792685', 
              'client_secret': 'f4eff24dbf324aea973a49f35931fdb1'
              ,'grant_type': 'authorization_code',
              'redirect_uri':'http://129.132.114.28:8080/locationhunter/homepage',
              'code':request.GET['code']}
        res = requests.post("https://api.instagram.com/oauth/access_token", data)
        login = json.loads(res.text)
        # here try to record the logged In token
        if userdao.hasPassword(login['user']['id']):
            inst = InstagramAPI(login['user']['username'],
                                userdao.getPassword(login['user']['id']))
            inst.login()
            if inst.isLoggedIn:
                login['uuid'] = inst.uuid
                login['csrf'] = inst.token
                global login_map
                login_map[str(login['user']['id'])] = inst
                print('Login Success')
            else:
                print('Login Failed')	
        request.session[login['user']['id']] = login;
        print(login)
    template = loader.get_template('hunterapp/homepage.html')
    context = {}
    context['username'] = login['user']['username']
    context['profile_pic'] = login['user']['profile_picture']
    response = HttpResponse(template.render(context, request))
    response.set_cookie('user_id', login['user']['id'])

    connect('locationhunter')
    logged_user = User.objects(user_id=login['user']['id'])
    profile_res = requests.get("https://api.instagram.com/v1/users/self/?access_token="
                           + login['access_token'])
    profile_text = profile_res.text
    user_profile = json.loads(profile_text)
    #update hashtags of user everytime he logs in
    getter_string = "https://api.instagram.com/v1/users/self/media/recent/?access_token="+login['access_token']
    profile_data = requests.get(getter_string).json()
    #profile data is now a dict
    media_list = profile_data['data']
    hashtag_list = []
    for media_post in media_list:
      to_parse = media_post['caption']
      if to_parse is not None:
        captiondata = to_parse['text']
        hashtag_list.extend(re.findall(r"#(\w+)", captiondata))
    return response


def userDetails(request):
    # here we store user data in mongodb if haven't before
    user_details = {}
    login = request.session[request.COOKIES['user_id']]
    profile_res = requests.get("https://api.instagram.com/v1/users/self/?access_token="
                               + login['access_token'])
    user_profile = json.loads(profile_res.text)
    # if expired
    if (user_profile.get('error_type')):
        user_details['error'] = 'Invalid Token'
        return HttpResponse(json.dumps(user_details))
    # query the user in monogoDB
    connect('locationhunter')
    logged_user = User.objects(user_id=user_profile['data']['id'])
    # get all hashtags of this user
    # get the data through instgram API
    recent_meida_url = "https://api.instagram.com/v1/users/self/media/recent/?access_token=" + login['access_token']
    profile_data = requests.get(recent_meida_url).json()
    # we get media_list
    media_list = profile_data['data']
    hashtag_list = []
    for media_post in media_list:
        to_parse = media_post['caption']
        if to_parse is not None:
            captiondata = to_parse['text']
            hashtag_list.extend(re.findall(r"#(\w+)", captiondata))
    # Update user vector representation everytime user log in or created
    userdao.updateUserVector(user_profile['data']['id'],hashtag_list)

 
    '''

    #Functionality to find related hashtags and add them ----> CUT HERE
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
    # -------> CUT UNTIL HERE
    '''

    # if user already in database
    if (logged_user):
        # update the information
        logged_user.update(username=user_profile['data']['username'],
                           num_followers=user_profile['data']['counts']['followed_by'],
                           num_followed_people=user_profile['data']['counts']['follows'],
                           media_count=user_profile['data']['counts']['media'],
                           profile_img_url=user_profile['data']['profile_picture'],
                           fullname=user_profile['data']['full_name'],
                           bio=user_profile['data']['bio'],
                           access_token=login['access_token'],
                           is_logged=True,
                           last_login=int(time.time()),
                           user_specific_hashtags=hashtag_list,
        )
        user_details = json.loads(logged_user[0].to_json())
        user_details['hashtags'] = userStatHelper.hashtagCount(user_details['user_specific_hashtags'])
        user_details['user_specific_hashtags'] = ''
        user_details['start_time'] = datetime.datetime.\
            fromtimestamp(logged_user[0].account_creation_time).date()\
            .strftime("%Y-%m-%d")
        
    else:
        # new the user
        new_user = User(user_id=login['user']['id'])
        new_user.username = user_profile['data']['username'];
        new_user.num_followers = user_profile['data']['counts']['followed_by']
        new_user.num_followed_people = user_profile['data']['counts']['follows']
        new_user.media_count = int(user_profile['data']['counts']['media'])
        new_user.profile_img_url = user_profile['data']['profile_picture']
        new_user.fullname = user_profile['data']['full_name']
        new_user.followed_people_list = []
        new_user.followers_list = []
        new_user.media_trend = []
        new_user.bio = user_profile['data']['bio']
        new_user.access_token = login['access_token']
        new_user.is_logged = True
        new_user.last_login = int(time.time())
        new_user.account_creation_time = int(time.time())
        new_user.followers_trend = []
        new_user.followed_people_trend = []
        new_user.user_specific_hashtags = []
        new_user.likes_trend = []
        new_user.user_specific_hashtags = hashtag_list
        new_user.declined_rec_users = []
        new_user.save()
        logged_user = User.objects(user_id=user_profile['data']['id'])
        user_details = json.loads(logged_user[0].to_json())
        user_details['hashtags'] = userStatHelper.hashtagCount(user_details['user_specific_hashtags'])
        user_details['user_specific_hashtags'] = ''
        user_details['start_time'] = datetime.datetime.fromtimestamp(
            logged_user[0].account_creation_time).date().strftime("%Y-%m-%d")

    #fetch user likes per tim
    list_of_dict = []
    for media_post in media_list:
      xx = (media_post['likes']['count'],media_post['created_time'])
      list_of_dict.append(xx)
      user_details['like_historic'] = list_of_dict
    return HttpResponse(json.dumps(user_details))
#GET
def locationTags(request,location):
    headers = {'Host': 'hashtagify.me',
               'Connection':'keep-alive',
               'Accept':'application/json, text/javascript, */*; q=0.01',
               'X-CSRF-Token':'9Ssfk0FIdQthHFSguv3ZFDrsD6L1KApYDm6/UtS8214=',
               'X-Requested-With':'XMLHttpRequest',
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
               'Referer':'http://hashtagify.me/',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'zh-CN,zh;q=0.8',
               'Cookie':'__uvt=; __utmt=1; __insp_wid=1647330093; __insp_nv=false; __insp_targlpu=https%3A%2F%2Fhashtagify.me%2Fpricing%3Fsource%3Dapi_pricing; __insp_targlpt=Hashtagify.me%20-%20Search%20And%20Find%20The%20Best%20Twitter%20Hashtags%20-%20Free; __insp_sid=2834659605; __insp_uid=2513694296; __insp_slim=1489852922608; __unam=657356c-15a67b75cf5-63783509-48; _hashtagify-pro_session=BAh7C0kiD3Nlc3Npb25faWQGOgZFVEkiJWVhMDUwNWE5NzU0M2MxOTI4NGQyMDFmZGE3N2ZmZjlkBjsAVEkiDmFidGVzdF9pZAY7AEZpBFb2MAFJIhB0YWJsZXRfdmlldwY7AEZGSSIQbW9iaWxlX3ZpZXcGOwBGRkkiEF9jc3JmX3Rva2VuBjsARkkiMTlTc2ZrMEZJZFF0aEhGU2d1djNaRkRyc0Q2TDFLQXBZRG02L1V0UzgyMTQ9BjsARkkiGXdhcmRlbi51c2VyLnVzZXIua2V5BjsAVFsHWwZpAvTjIiIkMmEkMTAkRjlXQVc1b0NFRmdoZzI3M1VhWUVDTw%3D%3D--9e4b033eae301e335d92847444c2e6d293d893ff; __utma=127509396.549915350.1487798755.1489338023.1489852460.7; __utmb=127509396.51.8.1489852927665; __utmc=127509396; __utmz=127509396.1489338023.6.5.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); days_hours_timezone=0; uvts=5gwaCB8M85VgKlwE',
               }
    r = requests.get('http://hashtagify.me/data/tags/'+location, headers=headers)
    return HttpResponse(r.text)


'''
def popularInfluencers(request):
    city = request.POST['city']
    country = request.POST['country']
    client = MongoClient('localhost', 27017)
    db = client.locationhunter
    collection = db.cities
    city = city.lower()
    city = unidecode(city)
    #print(country)
    #print(city)
    city_entity = collection.find_one({"country_id": country,"cities.name":city},{"cities":{"$elemMatch":{"name":city}}})
    if city_entity:
        location_id = city_entity['cities'][0]['top_location']['id']
        location_slug = city_entity['cities'][0]['slug']
        media_count_per_request = '100'
        max_number_of_posts_to_fetch = 30
        last_timestamp = 1490711000
        results = crawl_post_by_location.crawl_post_by_loc(location_id, location_slug, media_count_per_request,
                                    max_number_of_posts_to_fetch,last_timestamp)
        

        #here loop over media
        #serid, postcode, number_to_fetch, number_of_media_per_request
        
        ht_list = {}
        user_data_ass = {}
        for res in results:
          post_code = res['code']
          owner_id = res['owner']['id']
          get_data = crawl_user.fetch_posts_from_userid(owner_id,post_code,30,30)
          if get_data is None:
            continue #yes, C style continue. C > Python
          user_info = get_data[0]
          users_hashtags = []
          user_data_ass[owner_id] = user_info
          for media_post in get_data[1]:
            if 'caption' in media_post:
              my_captions = media_post['caption']
              hashtag_list = re.findall(r"#(\w+)", my_captions)
              users_hashtags.extend(hashtag_list)
              ht_list[owner_id] =  set(users_hashtags)

        connect('locationhunter')
        user_id = request.COOKIES['user_id']
        print(user_id)
        logged_user = User.objects(user_id=user_id)[0]
        print(logged_user)
        mytuple = (user_id,set(logged_user['user_specific_hashtags']))

        # here we should add something more
        return_junlin = recommend_user(ht_list,mytuple,5)
        front_end_data = []
        for candidate in return_junlin:
          myobj = {}
          myobj['user_data'] = user_data_ass[candidate[0]]
          myobj['score'] = candidate[1]
          front_end_data.append(myobj)

        #send the hashtags in a json to the front end

        #show the ranking and graphs
        return HttpResponse(json.dumps(front_end_data))
    else:
        data = {} 
        data['error'] = 'Invalid Country or City Name'
        json_data = json.dumps(data)
        return HttpResponse("error")
'''


def popularInfluencers(request):
    city = request.POST['city']
    country = request.POST['country']
    client = MongoClient('localhost', 27017)
    db = client.locationhunter
    collection = db.cities
    city = city.lower()
    city = unidecode(city)
    #print(country)
    #print(city)
    city_entity = collection.find_one({"country_id": country,"cities.name":city},{"cities":{"$elemMatch":{"name":city}}})
    if city_entity:
        pool = ThreadPool(32) # Use 32 threads in thread
        location_id = city_entity['cities'][0]['top_location']['id']
        location_slug = city_entity['cities'][0]['slug']
        media_count_per_request = '50'
        max_number_of_posts_to_fetch = 50
        last_timestamp = 1490711000
        results = crawl_post_by_location.crawl_post_by_loc(location_id, location_slug, media_count_per_request,
                                    max_number_of_posts_to_fetch,last_timestamp)
        

        #here loop over media
        #serid, postcode, number_to_fetch, number_of_media_per_request
                
        function_args = []
        for res in results:
          post_code = res['code']
          owner_id = res['owner']['id']
          function_args.append((owner_id, post_code, 50, 50))

        #print(function_args)
        function_results = pool.starmap(crawl_user.fetch_posts_from_userid, function_args)
        #close the pool and wait for the work to finish 
        pool.close() 
        pool.join() 

        #Filter the 'None' results
        filtered_function_results = []
        for result in function_results:
          if result is not None:
            filtered_function_results.append(result)

        ht_list = {}
        user_data_ass = {}
        for get_data in filtered_function_results:
          user_info = get_data[0]
          users_hashtags = []
          user_data_ass[user_info['userid']] = user_info
          for media_post in get_data[1]:
            if 'caption' in media_post:
              my_captions = media_post['caption']
              hashtag_list = re.findall(r"#(\w+)", my_captions)
              users_hashtags.extend(hashtag_list)
              ht_list[user_info['userid']] =  set(users_hashtags)
        #print(ht_list)
        print("Size of input: " + str(len(ht_list)))

        connect('locationhunter')
        user_id = request.COOKIES['user_id']
        print(user_id)
        logged_user = User.objects(user_id=user_id)[0]
        print(logged_user)
        mytuple = (user_id,set(logged_user['user_specific_hashtags']))


        return_junlin = recommend_user(ht_list,mytuple,5)
        front_end_data = []
        for candidate in return_junlin:
          myobj = {}
          myobj['user_data'] = user_data_ass[candidate[0]]
          myobj['score'] = candidate[1]
          front_end_data.append(myobj)

        #send the hashtags in a json to the front end

        #show the ranking and graphs
        return HttpResponse(json.dumps(front_end_data))
    else:
        data = {} 
        data['error'] = 'Invalid Country or City Name'
        json_data = json.dumps(data)
        return HttpResponse("error")




def privacypolicy(request):
  template = loader.get_template('hunterapp/privacypolicy.html')
  response = HttpResponse(template.render(request))
  return response;


# Space problem unsolved
def popularPost(request):
    city = request.POST['city']
    country = request.POST['country']
    client = MongoClient('localhost', 27017)
    db = client.locationhunter
    collection = db.cities
    city = city.lower()
    city = unidecode(city)
    city_entity = collection.find_one({"country_id": country,"cities.name":city},{"cities":{"$elemMatch":{"name":city}}})
    if city_entity:
        location_id = city_entity['cities'][0]['top_location']['id']
        location_slug = city_entity['cities'][0]['slug']
        media_count_per_request = '100'
        max_number_of_posts_to_fetch = 100
        last_timestamp = 1490711000
        results = crawl_post_by_location.crawl_post_by_loc(location_id, location_slug, media_count_per_request,
                                    max_number_of_posts_to_fetch,last_timestamp)
        connect('locationhunter')

        collection_match = CachedLocation.objects(location_id=city)
        newcached = []
        if not collection_match:
          #new location
          tstamp = int(time.time())
          newcached = CachedLocation(location_id=city, slug=location_slug,country_id=country,name=city,last_cached=tstamp)
          #for loop to add posts
        else:
          #exists, insert into list
          newcached = collection_match.first()

        comparetstamp = 0
        if newcached['cachedposts'] != []:
          comparetstamp = newcached['cachedposts'][-1]['date']

        print(comparetstamp)


        #for each post, we extract the hashtags  
        #only iterate if timestamp of latest cached_location < tstamp
        for doc_iter in reversed(results):
          if doc_iter['date'] > comparetstamp:
            to_parse = doc_iter.get('caption',"")
            hashtag_list = re.findall(r"#(\w+)", to_parse)
            instapost = InstagramPost(post_id=doc_iter.get('id'),hashtags=hashtag_list,code=doc_iter.get('code'),date=doc_iter.get('date'),width=doc_iter['dimensions']['width'],height=doc_iter['dimensions']['height'],caption=doc_iter.get('caption',""),comments_disabled=doc_iter.get('comments_disabled'),comments_count=doc_iter['comments']['count'],owner_id=doc_iter['owner']['id'],like_count=doc_iter['likes']['count'],display_src=doc_iter.get('display_src'))
            newcached.cachedposts.append(instapost)
        newcached.save()

       #call junlins algorithm with argument 'city
        list_of_lists = naive_recommend_hashtags(city,10) 
        print(json.dumps(list_of_lists))
        list_of_hashtag_ranking = [{'tag:':data[0], 'score':int(data[1]), 'count':int(data[2])} for data in list_of_lists]
        stringed_list_of_hashtag = ""

        my_json = json.dumps(list_of_hashtag_ranking,ensure_ascii=True)
        print(my_json)


        #send the hashtags in a json to the front end
 
        #show the ranking and graphs
        return HttpResponse(my_json)
    else:

        data = {} 
        data['error'] = 'Invalid Country or City Name'
        json_data = json.dumps(data)
        return HttpResponse("error")

#Because it's called with ajax
@csrf_exempt
def relatedHashtags(request):
  hashtag = request.POST['hashtag']
  header={'Host': 'i.instagram', 
              'X-IG-Capabilities': '36o=',
              'Cookie': 'csrftoken=dFhXHEBvUth6toAeIaVnNm8hkWaKCq3F; ds_user_id=3568831550; rur=ATN; s_network=""; is_starred_enabled=yes; igfl=data; sessionid=IGSC2bc67a82fc3bebf28a29f47b29a78ac8f5a9a5911838a6d047763c29f238e99c%3AOqjQBIkzMwbetApOh4h3XrYKcu92JYiQ%3A%7B%22_platform%22%3A0%2C%22_auth_user_id%22%3A3568831550%2C%22_auth_user_hash%22%3A%22%22%2C%22last_refreshed%22%3A1491483616.7723619938%2C%22asns%22%3A%7B%222001%3A67c%3A10ec%3A52c7%3A8000%3A%3A4c%22%3A559%2C%22time%22%3A1491483616%7D%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_token_ver%22%3A2%2C%22_token%22%3A%223568831550%3AO30E02IT3VldCXFyyACYViKOziR2sIe9%3Af65e5502d56eb58b0694738aabb028c4a4d368f12b1e795dc4a7f387a0dd4ed7%22%7D;ds_user=sulserfelipe; mid=V5E1YgAAAAEMbcRIM5TyLqE031df',
              'Connection':'keep-alive',
              'Accept':'*/*',
              'User-Agent':'Instagram 10.14.0 (iPhone8,1; iOS 10_2_1; en_CH; en-CH; scale=2.00; gamut=normal; 750x1334) AppleWebKit/420+',
              'Accept-Language':'en-CH;q=1, de-CH;q=0.9',
              'Accept-Encoding':'gzip, deflate',
              'X-IG-Connection-Type':'WiFi'}
  ress = requests.get("https://i.instagram.com/api/v1/tags/"+hashtag+"/related?related_types=[\"hashtag\"]",header)
  print(ress)
  return HttpResponse(ress)



def notification(request):
  template = loader.get_template('hunterapp/notification.html')
  connect('locationhunter')
  logged_user = User.objects(user_id=request.COOKIES['user_id'])[0]
  
  context = {'username':logged_user['username'],
              'profile_pic':logged_user['profile_img_url']}
  return HttpResponse(template.render(context, request))
        
def map_page(request,reqtype):
    template = loader.get_template('hunterapp/map_page.html')
    login = request.session[request.COOKIES['user_id']]   
    context = {"type":reqtype}
    context['username'] = login['user']['username']
    context['profile_pic'] = login['user']['profile_picture']
    return HttpResponse(template.render(context,request))
def tagSearch(request):
    template = loader.get_template('hunterapp/homepage-deprecated.html')
    context = {}
    return HttpResponse(template.render(context, request))

def postemail(request):
  if(request.method == 'POST'):
    print(request.POST)
    template = loader.get_template('hunterapp/homepage.html')
    connect('locationhunter')

    logged_user = User.objects(user_id=request.COOKIES['user_id'])[0]
    logged_user.update(email=request.POST['myemail'])
    context = {'username':logged_user['username'],
              'profile_pic':logged_user['profile_img_url']}
    return HttpResponse(template.render(context, request)) 
  else:
    return HttpResponse("You called the wrong method in views")

@csrf_exempt
def fof(request):
    # we want to do the recommendation everytime user log in, not every time they refresh
    # here we get user id
    user_id = request.COOKIES['user_id']
    if 'user' in request.POST:
        num = 4
        recs = []
        for i in range(num):
            pid = userdao.randomPickFollowingPeople(user_id)
            if pid == "":
              return HttpResponse("")
            rec = userInstgramProxy.getOneFollowee(pid)
            if rec != None and not userdao.alreadyFollowing(user_id,rec['user_id'])\
                    and rec['user_id'] != user_id:
                recs.append(rec)
        filtered = userdao.fliterDeclinedUser(request.POST['user'], recs)
        return HttpResponse(json.dumps(filtered))
    else:
        return HttpResponse("Error happened")

@csrf_exempt
def similarFof(request):
  connect('locationhunter')
  user_id = request.COOKIES['user_id']
  logged_user = User.objects(user_id=user_id)[0]
  user_id = request.COOKIES['user_id']
  counter = 0
  for rec_user in logged_user.fof:
    if rec_user['is_valid'] == 1:
      counter = counter+1
  if counter <= 0:
    if 'user' in request.POST:
        num = 10
        recs = []
        for i in range(num):
            pid = userdao.randomPickFollowingPeople(user_id)
            if pid == "":
              continue
            followees = userInstgramProxy.getFollowees(pid)
            if followees is not None:
              recs.extend(followees)
        #print("Found : " + str(len(recs)) + " followees")
        #Filter the already followed ones
        filtered_recs = []
        for r in recs:
          if not userdao.alreadyFollowing(user_id,r['user_id']):
            filtered_recs.append(r)
        filtered_recs = userdao.fliterDeclinedUser(request.POST['user'], recs)
        #print("After filtering : " + str(len(filtered_recs)) + " followees, taking max of 30 to compare")
        if(len(filtered_recs) > 30):
          recs = filtered_recs[0:29]
        else:
          recs = filtered_recs

        ht_list = {}
        user_data_ass = {}
        for rec in recs:
          owner_id = rec['user_id']
          post_code = "1"
          get_data = crawl_user.fetch_posts_from_userid(owner_id,post_code,30,30)
          if get_data is None:
            continue #yes, C style continue. C > Python
          user_info = get_data[0]
          users_hashtags = []
          user_data_ass[owner_id] = user_info
          for media_post in get_data[1]:
            if 'caption' in media_post:
              my_captions = media_post['caption']
              hashtag_list = re.findall(r"#(\w+)", my_captions)
              users_hashtags.extend(hashtag_list)
              ht_list[owner_id] =  set(users_hashtags)

       
        mytuple = (user_id,set(logged_user['user_specific_hashtags']))

        return_junlin = recommend_user(ht_list,mytuple,3)
        #send the hashtags in a json to the front end

        final_list = []
        for fe in return_junlin:
          r = userInstgramProxy.getOneFollowee(fe[0])

          if r is not None:
            r['is_valid'] = 1
            final_list.append(r)
        #print(json.dumps(final_list))
        #save it in db
        logged_user.update(fof = final_list)
        return HttpResponse(json.dumps(final_list))
    else:
        return HttpResponse("Error happened")
  else:
    final_list = []
    for rec_user in logged_user.fof:

      if rec_user['is_valid'] == 1 and \
              not userdao.alreadyFollowing(user_id,rec_user['user_id']):
        final_list.append(rec_user.to_mongo())
    #print(final_list)
    return HttpResponse(json.dumps(final_list))


@csrf_exempt
def similarLocation(request):
  connect('locationhunter')
  user_id = request.COOKIES['user_id']
  logged_user = User.objects(user_id=user_id)[0]
  user_id = request.COOKIES['user_id']
  counter = 0
  for rec_user in logged_user.recLoc:
    if rec_user['is_valid'] == 1:
      counter = counter+1
  if counter <= 0:
    #TODO: none are valid, need to execute the algorithm to pick 3-4 random locations from friends of friends
    print("To be implemented")
  
    if 'user' in request.POST:
        num = 10
        recs = []
        for i in range(num):
            pid = userdao.randomPickFollowingPeople(user_id)
            if pid == "":
              continue
            followees = userInstgramProxy.getFollowees(pid)
            if followees is not None:
              recs.extend(followees)
        print("Found : " + str(len(recs)) + " followees")
        #Filter the already followed ones
        filtered_recs = []
        for r in recs:
          if not userdao.alreadyFollowing(user_id,r['user_id']):
            filtered_recs.append(r)
        filtered_recs = userdao.fliterDeclinedUser(request.POST['user'], recs)
        #print("After filtering : " + str(len(filtered_recs)) + " followees, taking max of 30 to compare")
        if(len(filtered_recs) > 30):
          recs = filtered_recs[0:29]
        else:
          recs = filtered_recs

        location_list = []
        user_data_ass = {}
        counter = 0

        for rec in recs:
          owner_id = rec['user_id']
          post_code = "1"
          get_data = crawl_user.fetch_locations_from_userid(owner_id,rec['username'],20,20)
          if get_data is not None:
            location_list.append(get_data)
            if len(location_list) > 3:
              break
              
        print(json.dumps(location_list))
        #store in db
        logged_user.update(recLoc = location_list)
        return HttpResponse(json.dumps(location_list))
    else:
        return HttpResponse("Error happened")
  else:
    final_list = []
    for rec_loc in logged_user.recLoc:

      if rec_loc['is_valid'] == 1:
        final_list.append(rec_loc.to_mongo())
    #print(json.dumps(final_list))
    return HttpResponse(json.dumps(final_list))


@csrf_exempt
def fofAction(request):
    status = {}
    if 'related_name' in request.POST and 'related_id' in request.POST and 'action' in request.POST:
        user_id = request.COOKIES['user_id']
        if not request.session.has_key(user_id):
            status['type'] = 'No Session recorded'
        else:
            if request.POST['action'] == 'accept':
                if userdao.hasPassword(user_id):
                    user = request.session[user_id]
                    global login_map
                    inst = login_map[str(user['user']['id'])]
                    if inst.isLoggedIn:
                        inst.setMyUserId(user['user']['id'])
                        result =inst.follow(request.POST['related_id'])
                        if result:
                            userdao.invalidateRecFriend(user_id, request.POST['related_id'])
                            status['type'] = 'OK'
                        else:
                            status['type'] = 'Due to some reason,following failed'
                    else:
                        status['type'] = 'The password you provided might be wrong'
                else:
                    status['type'] = 'if you want to follow automatically, please fill in password in your settings'
            elif request.POST['action'] == 'decline':
                userdao.invalidateRecFriend(user_id,request.POST['related_id'])
                '''
                # move this stuff to userdao function
                logged_user = User.objects(user_id=user_id)[0]
                new_fof = []
                for data_x in logged_user.fof:
                  new_val = data_x.to_mongo()
                  if data_x['user_id'] == request.POST['related_id']:
                    new_val['is_valid'] = 0
                  new_fof.append(new_val)
            
                logged_user.update(fof = new_fof)
                userdao.recordDecline(user_id,request.POST['related_id'])
                '''
                status['type'] ='OK'
            else:
                status['type'] = 'Undefined Action'
    else:
        status['type'] = 'miss of parameter'
    return HttpResponse(json.dumps(status))

@csrf_exempt
def recLocationAction(request):
    status = {}
    if 'related_name' in request.POST and 'related_id' in request.POST and 'action' in request.POST:
        user_id = request.COOKIES['user_id']
        if not request.session.has_key(user_id):
            status['type'] = 'No Session recorded'
        else:
              #userdao.invalidateRecFriend(user_id,request.POST['related_id'])
              
              # move this stuff to userdao function
              logged_user = User.objects(user_id=user_id)[0]
              new_recLoc = []
              for data_x in logged_user.recLoc:
                new_val = data_x.to_mongo()
                if data_x['loc_id'] == request.POST['related_id']:
                  new_val['is_valid'] = 0
                new_recLoc.append(new_val)
          
              logged_user.update(recLoc = new_recLoc)
              #userdao.recordDecline(user_id,request.POST['related_id'])
              
              status['type'] ='OK'
       
    else:
        status['type'] = 'miss of parameter'
    return HttpResponse(json.dumps(status))


def settings(request):
    template = loader.get_template('hunterapp/setting.html')
    user = request.session[request.COOKIES['user_id']]
    #Get Email/ digest state from mongo
    connect('locationhunter')
    logged_user = User.objects(user_id=user['user']['id'])
    context = {'username': user['user']['username'],
               'profile_pic': user['user']['profile_picture'], 
		'email': logged_user[0]['email'], 
		'email_digest':logged_user[0]['email_digest'] }
    print(context)
    return HttpResponse(template.render(context, request))

def postPassword(request):
    if 'mypassword' in request.POST:
        user = request.session[request.COOKIES['user_id']]
        inst = InstagramAPI(user['user']['username'],request.POST['mypassword'])
        inst.login()
        if inst.isLoggedIn:
            userdao.updatePassword(user['user']['id'],inst.password)
            user['uuid'] = inst.uuid
            user['csrf'] = inst.token
            global login_map
            login_map[str(user['user']['id'])] = inst
            request.session[request.COOKIES['user_id']]=user
            return redirect("../homepage")
        else:
            return HttpResponse(user['user']['username']+","+request.POST['mypassword'])
    else:
        return HttpResponse("Password don't match")



def toggleEmailDigest(request):
	new_state = request.POST['digestState']
	print("New State: " + new_state)  
	user = request.session[request.COOKIES['user_id']]
	userid = user['user']['id']
	print(userid)	
	connect('locationhunter')
	logged_user = User.objects(user_id=userid)
	print(logged_user[0])
	logged_user[0].update(email_digest = new_state)
	print(logged_user[0]['email_digest'])
	logged_user[0].save()
	return HttpResponse("Success")


def updateEmail(request):
	new_email = request.POST['email']
	print("New Email: " + new_email)  
	user = request.session[request.COOKIES['user_id']]
	userid = user['user']['id']
	print(userid)	
	connect('locationhunter')
	logged_user = User.objects(user_id=userid)
	print(logged_user[0])
	logged_user[0].update(email = new_email)
	print(logged_user[0]['email'])
	logged_user[0].save()
	return HttpResponse("Success")


def responsivemap(request,reqtype):
  template = loader.get_template('hunterapp/responsivemap.html')
  context = {"type":reqtype}
  return HttpResponse(template.render(context,request))

def trips(request):
    if (('user_id' in request.COOKIES)
        and (request.session.has_key(request.COOKIES['user_id']))):
        template = loader.get_template('hunterapp/trips.html')
        login = request.session[request.COOKIES['user_id']]
        context = {}
        context['username'] = login['user']['username']
        context['profile_pic'] = login['user']['profile_picture']
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('hunterapp/login.html')
        context = {}
        return HttpResponse(template.render(context, request))

def responsivetrips(request):
  if (('user_id' in request.COOKIES)and (request.session.has_key(request.COOKIES['user_id']))):
    template = loader.get_template('hunterapp/responsivetrips.html')
    login = request.session[request.COOKIES['user_id']]
    context = {}
    context['username'] = login['user']['username']
    context['profile_pic'] = login['user']['profile_picture']
    return HttpResponse(template.render(context, request))
  else:
    template = loader.get_template('hunterapp/login.html')
    context = {}
    return HttpResponse(template.render(context, request))

def trips(request):
    if (('user_id' in request.COOKIES)
        and (request.session.has_key(request.COOKIES['user_id']))):
        template = loader.get_template('hunterapp/trips.html')
        login = request.session[request.COOKIES['user_id']]
        context = {}
        context['username'] = login['user']['username']
        context['profile_pic'] = login['user']['profile_picture']
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template('hunterapp/login.html')
        context = {}
        return HttpResponse(template.render(context, request))


def triprec(request, city):
    if request.session.has_key(request.COOKIES['user_id']):
        locs = locationdao.recLocations(city, request.COOKIES['user_id'])
        return HttpResponse(json.dumps(locs))
    else:
        return HttpResponse("Access Denied")


def avaCities(request):
    cities = locationdao.getAllCities('CH')
    return HttpResponse(json.dumps(cities))


@csrf_exempt
def genTrip(request):
    # TODO:Make Trip Route and Offer Feedback
    status = {}
    if ('locations[]' in request.POST
        and 'cities[]' in request.POST
        and 'curr_loc' in request.POST
        and 'accept_ids[]' in request.POST
        and 'decline_ids[]' in request.POST
        and request.session.has_key(request.COOKIES['user_id'])):
        # Those are for Trip Planning
        locations = request.POST.getlist('locations[]')
        cities = set(request.POST.getlist('cities[]'))
        curr_loc = request.POST['curr_loc']
        cities.add(curr_loc)
        # Those two for feedback
        accept_ids = request.POST.getlist('accept_ids[]')
        decline_ids = request.POST.getlist('accept_ids[]')
        locationdao.allocateFeedBacks(accept_ids, decline_ids,
                                      request.COOKIES['user_id'])
        print(cities)
        status['type'] = 'OK'


    else:
        status['type'] = 'Miss Parameters'
    return HttpResponse(json.dumps(status))


@csrf_exempt
def feedback(request):
    # TODO:Record User Feedbacks
    status = {}
    status['type'] = 'OK'
    return HttpResponse(json.dumps(status))
    

@csrf_exempt
def logAction(request, user, reqType, action):
    connect('locationhunter')
    logged_user = User.objects(user_id=user)[0]

    if(reqType == "fof"):
        if(action == "accept" ):
            val = logged_user.numFofAccepted + 1
            logged_user.update(numFofAccepted = val)
        else:
            val = logged_user.numFofDismissed + 1
            logged_user.update(numFofDismissed = val)
    elif(reqType == "location"):
        if(action == "accept" ):
            val = logged_user.numLocationsAccepted + 1
            logged_user.update(numLocationsAccepted = val)
        else:
            val = logged_user.numLocationsDismissed + 1
            logged_user.update(numLocationsDismissed = val)
    else:
        print("Bad Requst")
    return HttpResponse("Success")


@csrf_exempt
def sendMessage(request):
  status = {}
  user_id = request.COOKIES['user_id']
  
  if not request.session.has_key(user_id):
    status['type'] = 'No Session recorded'
  elif not 'message' in request.POST:
    status['type'] = 'Empty message'
  else:
    status['type'] ='message sent'
    accountSid = 'ACa047710ee69a17e3696e0b75d6d75ff5'
    authToken = '5b6ce7d39fb4b64e03e748f0b3568101'
    client = Client(accountSid, authToken)
    myTwilioNumber = '41798073668'
    destCellPhone = userdao.getPhoneNumber(user_id)
    if destCellPhone is not None:
      message = client.api.account.messages.create(to=destCellPhone,
                                             from_=myTwilioNumber,
                                            body=request.POST['message'])
    else:
      status['type'] = 'no phone number'
    #print(request.POST['message'])
  return HttpResponse(json.dumps(status))

def sendPhonenumber(request):
  status = {}
  user_id = request.COOKIES['user_id']
  
  if not request.session.has_key(user_id):
    status['type'] = 'No Session recorded'
  elif not 'myphone' in request.POST:
    status['type'] = 'Please provide your number in the settings'
  else:
    phone_number = request.POST['myphone']
    userdao.updatePhoneNumber(user_id,phone_number)
    status['type'] ='Saved'

  return HttpResponse(json.dumps(status))


#https://www.instagram.com/graphql/query/?query_id=17874545323001329&id=4700633444&first=10
