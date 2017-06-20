#Script To Fetch Recent Media From A User's Profile
import pycurl
import zlib
from io import BytesIO
import re
import simplejson as json

def posts_to_hashtag_array(posts_array):
	results_array = []
	for post in posts_array:
		results_array.extend(re.findall(r"#(\w+)", post['caption']))

	return results_array

def fetch_posts_from_user(username, number_to_fetch, number_of_media_per_request):
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
		exit()
	else:
		print("User has a public profile")

	#Read Valuable State information
	user_id = webpage_object['user']['id']
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
	return posts_array
#print(posts_array)

#Testing the Function
username =  "9gag" #This is translated to an id later
number_to_fetch = 100
number_of_media_per_request = 10

results = fetch_posts_from_user(username, number_to_fetch, number_of_media_per_request)
print(posts_to_hashtag_array(results))
#with open('sample_response_influencers.json', 'w') as output_file:
#	json.dump(posts_array, output_file)
