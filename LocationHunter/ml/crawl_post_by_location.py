#Fetch Recent Media Associated with some instagram Location

import pycurl
import zlib
from io import BytesIO
import re
import simplejson as json

#Crawls a the most recent posts in some location
#Stops crawling either when timestamp is reached or When the number of fetched posts exceeds max_number_of_posts_to_fetch
def crawl_post_by_loc(location_id, location_slug, media_count_per_request,max_number_of_posts_to_fetch,last_timestamp):
	posts_array = []
	number_of_posts_left = max_number_of_posts_to_fetch

	#Initially Load the location webpage 
	buffer = BytesIO()
	c = pycurl.Curl()
	c.setopt(c.URL, 'https://www.instagram.com/explore/locations/'+ location_id + "/" + location_slug)
	#c.setopt(c.VERBOSE, True)
	c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
	c.setopt(c.FOLLOWLOCATION, True) #Follow redirects
	c.setopt(c.WRITEDATA, buffer)
	c.perform()

	webpage  = buffer.getvalue().decode("utf-8")
	#Extract media_after_id variable (to fetch recent photos , this value always changes)
	#This value is found from reading Part of the webpage
	matched = re.search("has_next_page\": true, \"end_cursor", webpage)
	media_after_id = ""
	if matched == None:
		c.close()
		return posts_array
	index = matched.end() +4 #Start Index
	while(webpage[index] != '"'):
		media_after_id += webpage[index]
		index += 1

	print ("initial media_after_id: " + media_after_id)
	while(number_of_posts_left > 0):
		#Fake AJAX request to the instagram server
		buffer = BytesIO() #Reset Buffer
		postfields = 'q=ig_location('+location_id+')+%7B+media.after('+media_after_id+'%2C+'+media_count_per_request+')+%7B%0A++count%2C%0A++nodes+%7B%0A++++__typename%2C%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++comments_disabled%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%2C%0A++++video_views%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=locations%3A%3Ashow&query_id='
		header = [
			'origin: https://www.instagram.com',
			'accept-encoding: gzip, deflate, br',
			'accept-language: en-US,en;q=0.8,ar;q=0.6',
			'x-requested-with: XMLHttpRequest',
			'cookie: mid=WJ731gALAAGLwbTIM8mHiLTpUytS; fbm_124024574287414=base_domain=.instagram.com; sessionid=IGSCfc8bccc37612b4524d0806c935950cdc16ab5848aeafbf99b06c6389c8d6b854%3AfrFCKttnM9ylXAiduppwsb03aTRP4P2s%3A%7B%22_auth_user_id%22%3A4712929548%2C%22_auth_user_backend%22%3A%22accounts.backends.CaseInsensitiveModelBackend%22%2C%22_auth_user_hash%22%3A%22%22%2C%22_token_ver%22%3A2%2C%22_token%22%3A%224712929548%3AAaUC0JCcJwsXFs29F69aecBjpVaGVr1O%3Af56a73dc5fd42d4380f0d048a02b611cdac4a61bba938e2e3945cfef9f34a0b4%22%2C%22_platform%22%3A4%2C%22last_refreshed%22%3A1493585022.5842542648%2C%22asns%22%3A%7B%22time%22%3A1493633551%2C%2262.12.154.122%22%3A15623%7D%7D; ig_vw=1366; ig_pr=1; fbsr_124024574287414=l252sylAZVquOsK7ke_r9EZDstaj0FFPFKD03HPQxR8.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUUIyWTBvM0pOZUEweEw0ZDRLYVZ3VVhLZTFmZnZXTWVva1dHSzRlV2tibU1CaFBNY3AyMHEtVjUxaE1TRExhVXdpdUJPREU1R0JGZjgtTDlUWHZ4NXpoelpqMkdkZjYySVFuVll3dHVjRTNOb0xxWXVmRkp4UG9FVEE0TXBTRnJPUkR4Y1g2Nm9DLWFsU2UxNzhuZVFqTkFmY204aV9Dc0dKaC05QTVpWFdNdHZqY0x2QkRoZmVkVWY1VnA3YUJUUHZLYndyMXNYc0l1dVdNU0dRbXhlcncteXZYbXFDZF91M2l3WEJHS19ldEJLclRNbnRDdDViLXdVTm5JWVNkczdrTWhlZTJRUDhhN1JrUGltS1Q2N1dLRHNxMkV5eG5fT1QxdXFqc3FOand0SVlOVmRsNzlzR3BkaFlRMmlhOS1RbG5VbTc5S09mbW44aUtGNno2aEczQXVxYnZzY2hYWWZPQTZBWG55dDZfaVEiLCJpc3N1ZWRfYXQiOjE0OTM2NDEwMjksInVzZXJfaWQiOiIxMDAwMDc3NjEyMjEzMjUifQ; s_network=""; csrftoken=bMnJX3GfFDBcjUFW3jJYcSKNMfhNF0tq; rur=FRC; ds_user_id=4712929548',
			'x-csrftoken: bMnJX3GfFDBcjUFW3jJYcSKNMfhNF0tq',
			'pragma: no-cache',
			'x-instagram-ajax: 1',
			'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
			'content-type: application/x-www-form-urlencoded',
			'accept: */*',
			'cache-control: no-cache',
			'authority: www.instagram.com',
			'referer: https://www.instagram.com/explore/locations/' + location_id + '/' + location_slug + '/'
		]
		c.setopt(c.URL, 'https://www.instagram.com/query/')
		c.setopt(c.WRITEDATA, buffer)
		c.setopt(c.HTTPHEADER, header)
		c.setopt(c.POSTFIELDS, postfields)
		c.perform()


		body = buffer.getvalue()
		#TODO: Make Sure Response is JSON by parsing Response Type Header
		#Decompress Zipped Response
		try:		
			decompressed_data=zlib.decompress(body, 16+zlib.MAX_WBITS)
		except:
			print("Error Decompressing data")
			c.close()
			return posts_array

		#Read Status
		json_response = json.loads(decompressed_data)
		if(json_response['status'] =="ok"):
			print ("Status is ok")
			#check if Timestamp has been reached
			number_of_posts_received = len(json_response['media']['nodes'])
			print ("Received : " + str(number_of_posts_received) + " posts")
			last_post_timestamp = int(json_response['media']['nodes'][0]['date'])
			if(last_timestamp > last_post_timestamp):
				print( "Time Limit Reached.")
				number_of_posts_left = 0 
			else:
				#find next end cursor
				media_after_id = json_response['media']['page_info']['end_cursor']
				number_of_posts_left -= number_of_posts_received 
				print ("Need " + str(number_of_posts_left) + " more ... please wait")
			#Append New Posts to Array
			posts_array.extend(json_response['media']['nodes'])
		else:
			print ("Some Error Ocurred : Please Contact System Administrater (Houssam)")
			number_of_posts_left = 0


	c.close()
	return posts_array


'''
#Example Usage
location_id = "49695104"
location_slug  = "brooklyn-bridge"
media_count_per_request = '40'  
max_number_of_posts_to_fetch = 20000
last_timestamp = 1490711
results = crawl_post_by_loc(location_id, location_slug,media_count_per_request,max_number_of_posts_to_fetch,last_timestamp)


with open('sample_response.json', 'w') as output_file:
	json.dump(results, output_file)
'''

