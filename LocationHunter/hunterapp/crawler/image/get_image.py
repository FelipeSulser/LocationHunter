import pycurl
import zlib
from io import BytesIO
import re
import simplejson as json
from io import StringIO
from bs4 import BeautifulSoup
import urllib
from multiprocessing.dummy import Pool as ThreadPool 
import codecs
import unicodedata
import urllib.parse



def updateImageUrl(location):
	location = json.loads(location)
	if "image_url" in location.keys():
		if(location['image_url'].find("yahoo.gif")  == -1):
			print("Already There & Not yahoo.gif")
			return location    #Do not parse, already has image
	try: 
		query = urllib.parse.urlencode({"p": location['name'].encode('utf-8') })
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
		#if(image_url.find("yahoo.gif") != -1):
			#print(location['name']  + " is bad")
			#of = open('page.html', 'w')
			#of.write(str(webpage))
			#exit()
			#image_url = soup3.findAll('img', attrs = {'src' : True})[1]['src']  #Skip to the next image

		print(location['name'] + " - " + image_url)
		location['image_url'] = image_url
		return location
	except Exception as ex:
		#Return the location without an image url if something crashes
		print("Fail: " + location['name'])
		print(ex)
		return location


with open('locations_full.json') as locs_file:
	content = locs_file.readlines()

'''
yahoo = 0 
for line in content:
	ll = json.loads(line)
	if(('image_url' in ll.keys()) and ll['image_url'].find("yahoo.gif")!= -1):
		yahoo +=1


print("Found : " + str(yahoo)  + " yahoo lines out of " + str(len(content)) + " lines")
'''
pool = ThreadPool(32) # Use 32 threads in thread
function_results = pool.map(updateImageUrl,content)
        #close the pool and wait for the work to finish 
pool.close() 
pool.join() 


#Write Output
output_file = codecs.open('locations_with_images.json', 'w', 'utf-8')
for res in function_results:
	output_file.write(json.dumps(res, ensure_ascii=False) + "\n")
