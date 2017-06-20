from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.locationhunter
city_table = db.city_locations
location_table = db.locations
country_table = db.cities
for city in city_table.find({}):
    locations = city['locations']
    city_id = city['city_id']
    city_entity = country_table.find({'cities.id':city_id},{'_id':0,
                    'cities':{"$elemMatch":{ 'id': city_id }}})
   
    city_name = city_entity[0]['cities'][0]['name']
    for location in locations:
        location_table.insert({'id':location['id'],'slug':location['slug']
                               ,'name':location['name'],'belong_city':city_name,
                               'belong_city_id':city_id})
        print('Saved')
