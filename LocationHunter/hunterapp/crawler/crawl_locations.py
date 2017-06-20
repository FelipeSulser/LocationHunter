#
#  Modified to Crawl Location Coordinates
#

import requests
import urllib
import simplejson as json
import sys
from bs4 import BeautifulSoup



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

#Get Countries & Country IDs in JSON Format
'''
countries = []
for i in range(1, 7):
	resp = S.post(LOC_URL, headers=h, data=dict(page=i))
	print resp.headers['Content-type']
	results = json.loads(resp.text)
	country_list = results["country_list"]
	for j in range(len(country_list)):
		countries.append(country_list[j])

with open('countries.txt', 'w') as outfile:
    json.dump(countries, outfile)
'''


MAX_COUNTRIES = 55  # Maximum number of countries to consume
MAX_CITY_PAGES = 4 #maximum number of city pages to read (per country)
#Get Cities
LL = []
with open('countries.txt') as data_file:
	cl = json.load(data_file)
	print(str(len(cl)) + " countries to consume")
	#for i in range(len(cl)):
	for i in range(MAX_COUNTRIES):  #Start with countries
		country_url = LOC_URL + "/" +  cl[i]['id'] + "/" + cl[i]['slug']
		print("Eating up : "  + country_url)
		dd = {}
		dd['slug'] = cl[i]['name']
		dd['name'] = cl[i]['name']
		dd['country_id'] = cl[i]['id']
		dd['cities'] = []
		for j in range(1, MAX_CITY_PAGES): 
			S.get(country_url)   #Dummy request to get JSON Data Later
			resp = S.post(country_url, headers=h, data=dict(page=j))
			#print resp.headers['Content-type']
			if(resp.headers['Content-type'] == "application/json"):
				#New List of cities
				cities_obj = json.loads(resp.text)
				for k in range(len(cities_obj['city_list'])):
					k_city = cities_obj['city_list'][k]
					k_city['name'] = k_city['name'].lower()
					k_city['name'] = k_city['name'].split(',')[0]

					#Get the most relevant Location for the city  --- Later Append the Full List
					CITY_URL = LOC_URL + "/" + k_city['id'] + "/" + k_city['slug']
					print("    " + CITY_URL)
					
					S.get(CITY_URL)  #Dummy request to ensure that the next result is JSON
					cityresp = S.post(CITY_URL, headers=h, data=dict(page=1))
					if(cityresp.headers['Content-type'] == "application/json"):
						cityresp_obj = json.loads(cityresp.text)
						top_location = cityresp_obj['location_list'][0]
						top_location['name'] = top_location['name'].lower()
						top_location['name'] = top_location['name'].split(',')[0]
						#Crawl Location HTML Page to extract the GPS Coordinates
						TOP_LOCATION_URL = LOC_URL + "/"  + top_location['id'] + "/" + top_location['slug'] ; 
						location_page_response = S.get(TOP_LOCATION_URL);
						soup3 = BeautifulSoup(location_page_response.text, "lxml")
						lon = soup3.findAll(attrs={"property":"place:location:longitude"})[0]['content']
						lat = soup3.findAll(attrs={"property":"place:location:latitude"})[0]['content']
						top_location['lon'] = lon
						top_location['lat'] = lat
						#Add this top location to the corresponding city
						cities_obj['city_list'][k]['top_location'] = top_location
				#print(cities_obj['city_list'])
				dd['cities'].extend(cities_obj['city_list'])
				#Check if there are more cities
				if(cities_obj['next_page'] is None):
					print("end of list")
					break  	
		LL.append(dd)

with open('cities.txt', 'w') as cities_file:
	json.dump(LL, cities_file)