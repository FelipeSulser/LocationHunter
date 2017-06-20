#Script To Fetch Recent Media From A User's Profile
import pycurl
import zlib
from io import BytesIO
import re
import simplejson as json
from unidecode import unidecode
import urllib.parse
from bs4 import BeautifulSoup
import urllib
import codecs
import unicodedata

def posts_to_hashtag_array(posts_array):
	results_array = []
	for post in posts_array:
		results_array.extend(re.findall(r"#(\w+)", post['caption']))

	#convert unicode to ascii
	for i in range(len(results_array)):
		results_array[i] = unidecode(results_array[i])

	return results_array

def fetch_posts_from_username(username, number_to_fetch, number_of_media_per_request):
	print("Crawling User: " +username + " & fetching : " + str(number_to_fetch) + " with :   " + str(number_of_media_per_request) + " /req")
	buffer = BytesIO()
	c = pycurl.Curl()

	#Load Page First
	c.setopt(c.URL, 'https://www.instagram.com/'+ username + '/?__a=1') #the last parameter is to fetch a json object first
	#c.setopt(c.VERBOSE, True)
	c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
	c.setopt(c.FOLLOWLOCATION, True) #Follow redirects
	c.setopt(c.WRITEDATA, buffer)
	c.perform()
	#c.close()
	webpage_response  = buffer.getvalue()

	#Check if user has private/public profile
	webpage_object = json.loads(webpage_response)
	if(webpage_object['user']['is_private']):
		print("User Has a Private Profile")
		return None
	else:
		print("User has a public profile")
		print("\n")

	#Read Valuable State information
	user_id = webpage_object['user']['id']

	user_frontend_data = {}
	user_frontend_data['userid'] = webpage_object['user']['id']
	user_frontend_data['profile_pic_url'] = webpage_object['user']['profile_pic_url']
	user_frontend_data['username'] = webpage_object['user']['username']
	user_frontend_data['url_link'] = 'https://www.instagram.com/'+ username;
	

	posts_array = webpage_object['user']['media']['nodes'] #Add Loaded Posts
	number_of_posts_left = number_to_fetch - len(posts_array)
	print("Fetched : " + str(len(posts_array)) + " still " + str(number_of_posts_left) + " to go ... ")
	has_more_posts = webpage_object['user']['media']['page_info']['has_next_page']
	media_after_id = webpage_object['user']['media']['nodes'][len(posts_array)-1]['id']
	print("Last Post id is : " + str(media_after_id))

	while(number_of_posts_left > 0 and has_more_posts):
		
		#Clear Buffer
		buffer = BytesIO() #Reset Buffer

		postfields = 'q=ig_user('+str(user_id)+')+%7B+media.after('+str(media_after_id)+'%2C+'+str(number_of_media_per_request)+')+%7B%0A++count%2C%0A++nodes+%7B%0A++++__typename%2C%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++comments_disabled%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%2C%0A++++video_views%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=users%3A%3Ashow&query_id=17849115430193904'

		header = [  'origin: https://www.instagram.com' ,
					'accept-encoding: gzip, deflate, br' ,
					'accept-language: en-US,en;q=0.8,ar;q=0.6', 
					'x-requested-with: XMLHttpRequest' ,
					'cookie: mid=WLAvVgAEAAEkRy84UFEI3MN3fn4T; fbm_124024574287414=base_domain=.instagram.com; ig_dru_dismiss=1491927144420; ig_vw=503; ig_pr=1.100000023841858; csrftoken=Bog7r3G0qEOHtaB7CSFc1HsaU39XrhNT; rur=FRC; s_network=""' ,
					'x-csrftoken: Bog7r3G0qEOHtaB7CSFc1HsaU39XrhNT' ,
					'pragma: no-cache' ,
					'x-instagram-ajax: 1' ,
					'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36' ,
					'content-type: application/x-www-form-urlencoded' ,
					'accept: */*' ,
					'cache-control: no-cache' ,
					'authority: www.instagram.com' ,
					'referer: https://www.instagram.com/9gag/'  
		]

		c.setopt(c.URL, 'https://www.instagram.com/query/')
		c.setopt(c.WRITEDATA, buffer)
		c.setopt(c.HTTPHEADER, header)
		c.setopt(c.POSTFIELDS, postfields)
		c.perform()


		body = buffer.getvalue()
		#print (body)

		#Decompress Zipped Response
		decompressed_data=zlib.decompress(body, 16+zlib.MAX_WBITS)
		#print(decompressed_data)
		new_object = json.loads(decompressed_data)
		if(new_object['status'] == "ok"):
			print ("Status is Ok")
			number_of_posts_received = len(new_object['media']['nodes'])
			#Append Results
			posts_array.extend(new_object['media']['nodes'])
			#Update State Variables	
			media_after_id =  new_object['media']['page_info']['end_cursor']
			print("Media After: " + media_after_id)
			number_of_posts_left -= number_of_posts_received
			print(str(number_of_posts_left) + " posts left to ingest")
			has_more_posts = new_object['media']['page_info']['has_next_page']
		else:
			print ("An Error has ocurred ")
			break


	c.close()
	to_ret = [user_frontend_data,posts_array]
	return to_ret
#print(posts_array)

def fetch_locations_from_username(username, number_to_fetch, number_of_media_per_request):
	print("Crawling User: " +username + " & fetching : " + str(number_to_fetch) + " with :   " + str(number_of_media_per_request) + " /req")
	buffer = BytesIO()
	c = pycurl.Curl()

	#Load Page First
	c.setopt(c.URL, 'https://www.instagram.com/'+ username + '/?__a=1') #the last parameter is to fetch a json object first
	#c.setopt(c.VERBOSE, True)
	c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
	c.setopt(c.FOLLOWLOCATION, True) #Follow redirects
	c.setopt(c.WRITEDATA, buffer)
	c.perform()
	#c.close()
	webpage_response  = buffer.getvalue()

	#Check if user has private/public profile
	webpage_object = json.loads(webpage_response)
	if(webpage_object['user']['is_private']):
		print("User Has a Private Profile")
		return None
	else:
		print("User has a public profile")
		print("\n")

	#Read Valuable State information
	user_id = webpage_object['user']['id']

	user_frontend_data = {}
	user_frontend_data['userid'] = webpage_object['user']['id']
	user_frontend_data['profile_pic_url'] = webpage_object['user']['profile_pic_url']
	user_frontend_data['username'] = webpage_object['user']['username']
	user_frontend_data['url_link'] = 'https://www.instagram.com/'+ username;
	

	posts_array = webpage_object['user']['media']['nodes'] #Add Loaded Posts
	number_of_posts_left = number_to_fetch - len(posts_array)
	print("Fetched : " + str(len(posts_array)) + " still " + str(number_of_posts_left) + " to go ... ")
	has_more_posts = webpage_object['user']['media']['page_info']['has_next_page']
	if has_more_posts:
		media_after_id = webpage_object['user']['media']['nodes'][len(posts_array)-1]['id']
		print("Last Post id is : " + str(media_after_id))

	myLoc = {}

	while(number_of_posts_left > 0 and has_more_posts):
		
		#Clear Buffer
		buffer = BytesIO() #Reset Buffer

		postfields = 'q=ig_user('+str(user_id)+')+%7B+media.after('+str(media_after_id)+'%2C+'+str(number_of_media_per_request)+')+%7B%0A++count%2C%0A++nodes+%7B%0A++++__typename%2C%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++comments_disabled%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%2C%0A++++video_views%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=users%3A%3Ashow&query_id=17849115430193904'

		header = [  'origin: https://www.instagram.com' ,
					'accept-encoding: gzip, deflate, br' ,
					'accept-language: en-US,en;q=0.8,ar;q=0.6', 
					'x-requested-with: XMLHttpRequest' ,
					'cookie: mid=WLAvVgAEAAEkRy84UFEI3MN3fn4T; fbm_124024574287414=base_domain=.instagram.com; ig_dru_dismiss=1491927144420; ig_vw=503; ig_pr=1.100000023841858; csrftoken=Bog7r3G0qEOHtaB7CSFc1HsaU39XrhNT; rur=FRC; s_network=""' ,
					'x-csrftoken: Bog7r3G0qEOHtaB7CSFc1HsaU39XrhNT' ,
					'pragma: no-cache' ,
					'x-instagram-ajax: 1' ,
					'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36' ,
					'content-type: application/x-www-form-urlencoded' ,
					'accept: */*' ,
					'cache-control: no-cache' ,
					'authority: www.instagram.com' ,
					'referer: https://www.instagram.com/9gag/'  
		]

		c.setopt(c.URL, 'https://www.instagram.com/query/')
		c.setopt(c.WRITEDATA, buffer)
		c.setopt(c.HTTPHEADER, header)
		c.setopt(c.POSTFIELDS, postfields)
		c.perform()


		body = buffer.getvalue()
		#print (body)

		#Decompress Zipped Response
		decompressed_data=zlib.decompress(body, 16+zlib.MAX_WBITS)
		#print(decompressed_data)
		new_object = json.loads(decompressed_data)
		if(new_object['status'] == "ok"):
			print ("Status is Ok")
			listOfPosts = new_object['media']['nodes']

			if(len(listOfPosts)==0):  #Sometimes the server just sends 0 posts with status OK
				continue 
			number_of_posts_left -= len(listOfPosts)
			for myPost in listOfPosts:
				#print(myPost['code'])
				MY_POST_URL = "www.instagram.com/p/" + myPost['code'] + "/?__a=1"
				print(MY_POST_URL)
				buffer2 = BytesIO()
				c2 = pycurl.Curl()

				#Load Page First
				c2.setopt(c2.URL, MY_POST_URL) #the last parameter is to fetch a json object first
				#c.setopt(c.VERBOSE, True)
				c2.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
				c2.setopt(c2.FOLLOWLOCATION, True) #Follow redirects
				c2.setopt(c2.WRITEDATA, buffer2)
				c2.perform()
				#c.close()
				webpage_response2  = buffer2.getvalue() 

				#Check if user has private/public profile
				webpage_object2 = json.loads(webpage_response2)

				#print(json.dumps(webpage_object2['graphql']['shortcode_media']))
				if('location' in webpage_object2['graphql']['shortcode_media'] and webpage_object2['graphql']['shortcode_media']['location'] != None):
					webpage_object2['graphql']['shortcode_media']['location']['img_url'] = webpage_object2['graphql']['shortcode_media']['display_url']
					return webpage_object2['graphql']['shortcode_media']['location']
				else:
					print("Failed extracting data")


			#print(json.dumps(new_object))
			
		else:
			print ("An Error has ocurred ")
			break

	return None
	#c.close()
	#to_ret = [user_frontend_data,posts_array]
	#return to_ret
#print(posts_array)

#This needs the postcode to translate a userid to a username
def fetch_posts_from_userid(userid, postcode, number_to_fetch, number_of_media_per_request):
	POST_URL = "www.instagram.com/p/" + postcode + "/?__a=1"
	buffer = BytesIO()
	c = pycurl.Curl()

	#Load Page First
	c.setopt(c.URL, POST_URL) #the last parameter is to fetch a json object first
	#c.setopt(c.VERBOSE, True)
	c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
	c.setopt(c.FOLLOWLOCATION, True) #Follow redirects
	c.setopt(c.WRITEDATA, buffer)
	c.perform()
	#c.close()
	webpage_response  = buffer.getvalue()

	#Check if user has private/public profile
	webpage_object = json.loads(webpage_response)
	#print(json.dumps(webpage_object['graphql']))
	username = webpage_object['graphql']['shortcode_media']['owner']['username']
	results = fetch_posts_from_username(username, number_to_fetch, number_of_media_per_request)
	return results

#This needs the postcode to translate a userid to a username
def fetch_locations_from_userid(userid, postcode, number_to_fetch, number_of_media_per_request):
	username = postcode
	results = fetch_locations_from_username(username, number_to_fetch, number_of_media_per_request)
	if results is None:
		return None
	print("Results \n\n\n")
	print(results)
	ret_dic = {}
	ret_dic['img_url'] = results['img_url']
	ret_dic['loc_id'] = results['id']
	ret_dic['user_id'] = userid
	ret_dic['is_valid'] = 1
	ret_dic['name'] = results['name']
	ret_dic['region'] = results['name']
	ret_dic['username'] = username

	#Try to get a better image from Yahoo
	try:
		print("trying : "+ ret_dic['name'])
		query = urllib.parse.urlencode({"p": ret_dic['name'].encode('utf-8') })
		YAHOO_IMG_URL  = "https://images.search.yahoo.com/search/images;_ylt=AwrB8p0b_A1ZnQYAqouLuLkF;_ylc=X1MDOTYwNTc0ODMEX3IDMgRiY2sDMHNoYzV1MWNnZ20xZiUyNmIlM0QzJTI2cyUzRGliBGZyAwRncHJpZAN4YjJRRFBLLlRIR0paSElNZld4NlJBBG10ZXN0aWQDbnVsbARuX3N1Z2cDMTAEb3JpZ2luA2ltYWdlcy5zZWFyY2gueWFob28uY29tBHBvcwMwBHBxc3RyAwRwcXN0cmwDBHFzdHJsAzQEcXVlcnkDcGljdAR0X3N0bXADMTQ5NDA4ODg1MgR2dGVzdGlkA251bGw-?gprid=xb2QDPK.THGJZHIMfWx6RA&pvid=2KkqJTY5LjEORYXwWQhYLwNcNjIuMQAAAACkFxg8&fr2=sb-top-images.search.yahoo.com&"+query+"&ei=UTF-8&iscqry=&fr=sfp"

		buffer = BytesIO()
		c = pycurl.Curl()
		c.setopt(c.URL, YAHOO_IMG_URL)
		c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
		c.setopt(c.WRITEDATA, buffer)
		c.perform()

		webpage  = buffer.getvalue()
		soup3 = BeautifulSoup(webpage, "lxml")
		image_url = soup3.findAll('img', attrs = {'src' : True})[0]['src']
		if(image_url.find("yahoo.gif") != -1):
			print("Bad page from yahoo")
		else:
			ret_dic['img_url'] = image_url
			print("Image successfully stolen from yahoo")
	except Exception as ex:
		print(ex)
		print("Failed to Find a Better Image")		


	return ret_dic


'''
#Testing the Function
username =  "9gag" #This is translated to an id later
number_to_fetch = 100
number_of_media_per_request = 40

#results = fetch_posts_from_user(username, number_to_fetch, number_of_media_per_request)
#print(posts_to_hashtag_array(results))
#res = fetch_posts_from_userid("327771661", "BSyQD0dDg8X", number_to_fetch, number_of_media_per_request)
res = fetch_posts_from_userid("327771661", "1", number_to_fetch, number_of_media_per_request)

print(res)

#with open('sample_response_influencers.json', 'w') as output_file:
#	json.dump(posts_array, output_file)

'''