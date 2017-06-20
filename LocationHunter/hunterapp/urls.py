'''
Created on 2017年3月18日

@author: 123
'''
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.welcome, name='welcome'),
    url(r'^direct/$', views.direct, name='direct'),
    url(r'^homepage/$', views.homepage, name='homepage'),
    url(r'^user/details/$', views.userDetails, name='userdetails'),
    url(r'^locationtags/(?P<location>[\s\S]+)/$',views.locationTags,name='locationTags'),
    #url(r'^trips/$',views.tripRecommendation,name='tripRecommendation'),
    #url(r'^partners/$',views.partnerRecommendation,name='partnerRecommendation'),
    url(r'^login/$',auth_views.login,kwargs={'template_name':'login.html'},name='login'),
    url(r'^logout/$',auth_views.logout,kwargs={'next_page':'/'},name='logout'),  
    url(r'^privacypolicy/$',views.privacypolicy,name='privacypolicy'),
    url(r'^popularPost/$',views.popularPost,name='popularPost'),
    url(r'^popularInfluencers/$',views.popularInfluencers,name='popularInfluencers'),
    url(r'^map_page/(?P<reqtype>[\s\S]+)/$',views.map_page,name='map_page'),
    url(r'^notification/$',views.notification,name='notification'), 
    url(r'^post-email/$',views.postemail,name='postemail'), 
    url(r'^fof/$',views.fof,name='fof'),
    url(r'^similarFof/$',views.similarFof,name='similarFof'),
    url(r'^similarLocation/$',views.similarLocation,name='similarLocation'),
    url(r'fof/action/',views.fofAction,name="fofAction"),
    url(r'recLocations/action/',views.recLocationAction,name="recLocationAction"),
    url(r'settings/',views.settings,name='settings'),
    url(r'^post-password/$',views.postPassword,name='post-password'),
    url(r'^relatedHashtags/$',views.relatedHashtags,name='relatedHashtags'),
    url(r'^toggleEmailDigest/$',views.toggleEmailDigest,name='toggleEmailDigest'),
    url(r'^updateEmail/$',views.updateEmail,name='updateEmail'),
    url(r'^trips/$', views.trips, name='trip'),
    url(r'^responsivetrips/$', views.responsivetrips, name='responsivetrips'),
    url(r'^triprec/(?P<city>[\s\S]+)/$', views.triprec, name='triprec'), 
    url(r'^avaCities/$', views.avaCities, name='avaCities'),
    url(r'^genTrip/$', views.genTrip, name='genTrip'),
    url(r'^feedback/$', views.feedback, name='feedback'),
    url(r'^google486a122b04c93dd1',views.verification, name='verification'),
    url(r'^logAction/(?P<user>[\s\S]+)/(?P<reqType>[\s\S]+)/(?P<action>[\s\S]+)/$', views.logAction, name='logAction'),
    url(r'^adminLogging/$', views.adminLogging, name='adminLogging'),
    url(r'^sendMessage/$', views.sendMessage, name='sendMessage'),
    url(r'^sendPhonenumber/$', views.sendPhonenumber, name='sendPhonenumber'),
    


]
