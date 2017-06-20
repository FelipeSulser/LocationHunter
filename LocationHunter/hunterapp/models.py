from django.db import models
from mongoengine import *
# Create your models here.

class TrendData(EmbeddedDocument):
	date = IntField()
	value = IntField()
class UserRecomended(EmbeddedDocument):
	date = IntField()
	user_id = StringField()
class Followee(EmbeddedDocument):
	full_name = StringField()
	id = StringField()
	followed_by_viewer = BooleanField()
	is_verified = BooleanField()
	profile_pic_url = StringField()
	requested_by_viewer = BooleanField()
	username = StringField()

class FriendOfFriend(EmbeddedDocument):
	username = StringField()
	img_url = StringField()
	user_id = StringField()
	is_valid = IntField()

class TargetLocation(EmbeddedDocument):
	loc_id = StringField()
	img_url = StringField()
	user_id = StringField()
	is_valid = IntField()
	name = StringField()
	region = StringField()
	username = StringField()

class User(Document):
	# update every time you log in the database
	user_id = StringField(required=True,unique=True)
	username = StringField(required=True, unique=True)
	email_digest = StringField()
	email = StringField()
	num_followers = IntField()
	num_followed_people = IntField()
	profile_img_url = StringField()
	fullname = StringField()
	# unable to get it by far
	followers_list = ListField(StringField())
	followed_people_list = ListField(EmbeddedDocumentField(Followee))
	# update at night when log in simply read
	followers_trend = ListField(EmbeddedDocumentField(TrendData))
	followed_people_trend = ListField(EmbeddedDocumentField(TrendData))
	# update every time you log in the database
	bio = StringField()
	access_token = StringField()
	is_logged = BooleanField()
	last_login = IntField()
	# no idea so far
	user_specific_hashtags = ListField(StringField())
	# now added field
	account_creation_time = IntField()
	media_count = IntField()
	media_trend = ListField(EmbeddedDocumentField(TrendData))
	likes_trend = ListField(EmbeddedDocumentField(TrendData))
	# record all the recommended paterners to the users on which the user has declined
	declined_rec_users = ListField(EmbeddedDocumentField(UserRecomended))
	# accepted_rec_users = ListField(EmbeddedDocumentField(UserRecomended))
	# in order to do advanced functions
	password = StringField()
	phone_number = StringField()
	fof = ListField(EmbeddedDocumentField(FriendOfFriend))
	recLoc = ListField(EmbeddedDocumentField(TargetLocation))
	numFofAccepted = IntField()
	numFofDismissed = IntField()
	numLocationsAccepted = IntField()
	numLocationsDismissed = IntField()


class Location(Document):
	latitude = StringField()
	longitude = StringField()
	name = StringField()
	
class Media(Document):
	text = StringField()
	hashtags = ListField(StringField())
	location = ReferenceField(Location)
	liked_by = ListField(StringField())
class TopLoc(EmbeddedDocument):
	slug = StringField()
	id = StringField()
	name = StringField()
class City(EmbeddedDocument):
	slug = StringField()
	top_location = EmbeddedDocumentField(TopLoc)
	name = StringField()
	id = StringField()

class cities(Document):
	cities = ListField(EmbeddedDocumentField(City))
	slug = StringField()
	country_id = StringField()
	name = StringField()
	valid = StringField()

class InstagramPost(EmbeddedDocument):
	post_id = StringField()
	code = StringField()
	width = IntField()
	height = IntField()
	caption = StringField()
	comments_disabled = BooleanField()
	comments_count = IntField()
	owner_id = StringField()
	like_count = IntField()
	date = IntField()
	display_src = StringField()
	is_video = BooleanField()
	video_views = IntField()
	hashtags = ListField(StringField())
class CachedLocation(Document):
	location_id = StringField()
	cachedposts = ListField(EmbeddedDocumentField(InstagramPost))
	slug = StringField()
	country_id = StringField()
	name = StringField()
	last_cached = IntField()