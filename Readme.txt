Django:

Superuser <user,pwd>: <islab2017, team12345678>


To persist in MongoDB:
	- Need to define the model in models.py
	- Once defined, in views when trying to persist data do the following
	- connect('db_name') --> in our case "locationhunter"
	- user = User(username="", attrib="", attrib2="")
	- user.save() -> this saves it into mongo 
	- We have data orthogonality!

To query MongoDB:
	- connect('db_name')
	- collection = <name_collection>.objects(field="attribute")
	- for more information: http://docs.mongoengine.org/guide/querying.html


Add CSS/JS files to Django templates:
	- Add css file in static directory of project
	- Write {% load static %} in the beginning of the template
	- <link href="{% static 'hunterapp/css/style.css' %}" rel="stylesheet"> to make the reference

	
MySQL:

Database name: locationhunter

<User,Password>: <root,1234>, <test,test>

To stop MySQL server: sudo service mysql stop

To run it again: sudo service mysql start

MongoDB:

To start mongo, write mongo.

If mongo instance is down, re run it with "nohup mongod &"

To import a list of json documents to mongo

mongoimport --db taac --collection july2012 lariatData-sgeT-2012-07-02.json --jsonArray


Gmail (used for sending digests):
locationhunterapp@gmail.com
password: team404@@