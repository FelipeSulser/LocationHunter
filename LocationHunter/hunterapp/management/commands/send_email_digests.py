from  django.core.management.base  import  BaseCommand
from django.db import connection
from django.core.mail import EmailMessage
from hunterapp.models import *
from mongoengine import *
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import matplotlib as mpl
mpl.use('Agg')  #Disable display
import matplotlib.pyplot as plt
import numpy as np


#Read last two entries from the array and calculate the trend
def getTrendLine(arr, title):
	l = len(arr)
	strn = ""		
	if(l >= 2):
		strn = "<h3>"+ title + ": "
		diff = int(100.0*(arr[l-1]['value']-arr[l-2]['value'])/arr[l-2]['value'])
		sgn = ""		
		if(diff > 0 ):
			sgn = "+"
		strn = strn + str(arr[l-1]['value']) +  " (" +sgn + str(diff) + " %) <h3/>"  
	return strn

def attachGraph(valuesArray, maxPoints, msg, username, imgName):
	try:
		#Create
		trend_count = min(maxPoints, len(valuesArray))
		x = np.linspace(1, trend_count, trend_count)
		follower_tuples = np.array(valuesArray)[-trend_count:]
		values = []

		for ft in follower_tuples:
			values.append(ft['value'])
		
		plt.ioff()
		fig = plt.figure()
		plt.plot(x, values, label='linear')

		# Add a legend
		USER_FILE_PATH= "/plots/"+username + "/"
		if not os.path.isdir(USER_FILE_PATH):
			#Create a folder in plots
			os.makedirs(USER_FILE_PATH)

		fig.savefig(USER_FILE_PATH + imgName)
		plt.close(fig)
		print("Saved figure : "+ imgName)

		#Now Attach to Email
		fp = open(USER_FILE_PATH + imgName, 'rb')
		msg_img = MIMEImage(fp.read())
		fp.close()
		msg_img.add_header('Content-ID', '<'+imgName+'>')
		msg.attach(msg_img)
		print("Attached")
		return True #Succeeded
	except Exception as ex:
		print("Failed to save image" + imgName)
		print(ex)
		return False


class Command(BaseCommand):
	def handle(self,**options):
		try:
			self.send_email_digests()
		except Exception as e:
			print(e)
		finally:
			connection.close()

	def send_email_digests(self):   
		connect('locationhunter')      
		for user in User.objects.all():
			if(user.email_digest == "on"):

				print("Preparing: " + user.username + "'s email ...")
				html_content = '<h2>Hi <b>%s</b>, here\'s your daily digest </h2><br/><br/>' % user.username
				loggedUser = User.objects(username=user.username)[0].to_mongo()
				toEmail = loggedUser['email']					
				
				#print(loggedUser.keys())
				if 'followers_trend' in loggedUser.keys():
					subject = 'Your Daily Digest'
					text_content = "This is random text"
					msg = EmailMultiAlternatives(subject, text_content,
					                             'Location Hunter', [toEmail])
					
					html_content += getTrendLine(loggedUser['followers_trend'],'Followers')
					if(attachGraph( loggedUser['followers_trend'], 21, msg, user.username,'followers.png')):
						html_content += "<img height='384' width='512' src='cid:followers.png'/>"
					html_content += getTrendLine(loggedUser['followed_people_trend'],'Followed People')
					if(attachGraph( loggedUser['followed_people_trend'], 21, msg, user.username,'followed_people_trend.png')):
						html_content += "<img height='384' width='512' src='cid:followed_people_trend.png'/>"
					html_content += getTrendLine(loggedUser['media_trend'],'Media')
					if(attachGraph( loggedUser['media_trend'], 21, msg, user.username,'media_trend.png')):
						html_content += "<img height='384' width='512' src='cid:media_trend.png'/>"


					#Closing Sentences
					html_content += "<br/><br/><p> Thank you for using Location Hunter,</p>"
					html_content += "<p>The Location Hunter Team </p>"
					print(html_content)

					msg.attach_alternative(html_content, "text/html")
					msg.mixed_subtype = 'related'

					#Send Email
					msg.send()
				else:
					print("This guy does not have followers_trend")