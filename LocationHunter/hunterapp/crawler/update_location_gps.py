# Multithreaded Program that reads a file with locations
#Retrieves their GPS Coordinates
#Stores them back in another file


import requests
import urllib
import simplejson as json
import sys
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool 

BASE = "https://www.instagram.com"
LOC_URL = BASE + "/explore/locations"
QUERY_URL = BASE + "/query/"

S = requests.Session()

h = {	'x-instagram-ajax':'1' , 
		'content-type': 'application/x-www-form-urlencoded', 
		'origin':'https://www.instagram.com',
		'pragma':'no-cache'
	}

#Load Locations Page first
resp = S.get(LOC_URL)
failed_ids = []
def updateCoords(line):
	line_obj = json.loads(line)
	object_locations = line_obj['locations']
	for ll in object_locations:
		URL_FOR_LOC = LOC_URL + "/"  + ll['id'] + "/"
		location_page_response = S.get(URL_FOR_LOC);
		soup3 = BeautifulSoup(location_page_response.text, "lxml")
		#print(len(soup3.findAll(attrs={"property":"place:location:longitude"})))
		if(len(soup3.findAll(attrs={"property":"place:location:longitude"})) ==1):
			lon = soup3.findAll(attrs={"property":"place:location:longitude"})[0]['content']
			lat = soup3.findAll(attrs={"property":"place:location:latitude"})[0]['content']
			#Update Location Object GPS Coordinates
			ll['lat'] = lat
			ll['lon'] = lon
			print(ll['id'] +  " : "  + lat + " - " + lon)
		else:
			failed_ids.append(ll['id'])
			print("Added a failed id")
	print("Finished 1 line... ")
	return line_obj['locations']
	#Write the modified locatiosn array on 1 line


with open('lh_locs.json') as locs_file:
	content = locs_file.readlines()


pool = ThreadPool(32) # Use 32 threads in thread
function_results = pool.map(updateCoords,content)
        #close the pool and wait for the work to finish 
pool.close() 
pool.join() 


#Write Output
output_file = open('locations_with_coords.json', 'w')
last_array = []
for res in function_results:
	last_array.extend(res)


output_file.write(json.dumps(last_array))

#Write the failed location ids
with open('failed_ids.txt', 'w') as failed_file:
	for ii in failed_ids:
		failed_file.write(ii+"\n")