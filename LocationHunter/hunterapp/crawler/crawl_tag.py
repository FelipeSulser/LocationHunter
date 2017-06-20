#Script To Fetch Recent Media Associated with a Certain Tag Name

import pycurl
import zlib
from StringIO import StringIO
import re


#ONLY TWO PARAMETERS NEEDED BELOW
tags = ['sun', 'sunday', 'life', 'matlab', 'book', 'uni', 'zurich', 'mensa', 'blue', 'summer', 'schoggi']

for i in range(100):
	tag_name =  tags[i%11]
	media_count = '10'


	buffer = StringIO()
	c = pycurl.Curl()

	#Load Page First
	c.setopt(c.URL, 'https://www.instagram.com/explore/tags/'+ tag_name)
	#c.setopt(c.VERBOSE, True)
	c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
	c.setopt(c.FOLLOWLOCATION, True) #Follow redirects
	c.setopt(c.WRITEDATA, buffer)
	c.perform()
	#c.close()
	webpage  = buffer.getvalue()

	#Extract media_after_id variable (to fetch recent photos, this value always changes)
	#This value is found from reading Part of the webpage

	matched = re.search("end_cursor", webpage)
	media_after_id = webpage[matched.end()+4:matched.end()+32]
	#print(media_after_id)

	buffer = StringIO() #Reset Buffer

	postfields = 'q=ig_hashtag('+tag_name+')+%7B+media.after('+media_after_id+'%2C+'+media_count+')+%7B%0A++count%2C%0A++nodes+%7B%0A++++__typename%2C%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++comments_disabled%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%2C%0A++++video_views%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=tags%3A%3Ashow&query_id='

	header = [ 'origin: https://www.instagram.com' ,
	 'accept-encoding: gzip, deflate, br' ,
	 'accept-language: en-US,en;q=0.8,ar;q=0.6' ,
	 'x-requested-with: XMLHttpRequest' ,
	 'cookie: mid=WLAvVgAEAAEkRy84UFEI3MN3fn4T; fbm_124024574287414=base_domain=.instagram.com; ig_dru_dismiss=1489245899094; fbsr_124024574287414=b1Lcf62YMiZbRbpccYsr6nFbGylx7ssBAdoTekWkMi8.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImNvZGUiOiJBUURHMTZBR0ExNTVSOGxIMDFtR2JHMExYWU5IcXdSajBidFkwX05DZlRRLTl4QVI3cjNPRW9fOXB1ZWZuLVBzZGZmMV9MQ3ZCZ0t2Z284Sno2SUxfTThfUTIzS0Z1d2FESFZYN0tpREVfZmd6b2l5clpLemEtc0xtN0ZYcXg3V3o5dE1TWXlRSzhRdWRfVVRqQmEyREl6ajJGTDYybUJ2cllSVzJOaUdYWTNYRHV3cXFSS3B3TjZNb0ZHcG5TLWpXRmlzbFI5UmkwdjFVcWlWQlNTMVdYQ0hCR3NDeGcyNng1ckd4Yll4SG1ET0JzSVJESThYenVpTkVVSmNXTkVrYVpOcnl1M1BqT1NjSkRvNHJKc3dNR29VbDNKcUxKNkVrODZ6SG1WSldDLU9ucDJueTdYRFhXeGpSZUFhZTNaT1AxYUtPR19ZZ0VIN1NTRVczeXNYYm8yUSIsImlzc3VlZF9hdCI6MTQ4OTE2NDYwNCwidXNlcl9pZCI6IjUwMTU5MDg4NCJ9; csrftoken=kKoQWz7d2KMyltke2OR3eNSwKHvPmiY0; s_network=""; ig_vw=527; ig_pr=1.25' ,
	 'x-csrftoken: kKoQWz7d2KMyltke2OR3eNSwKHvPmiY0' ,
	 'pragma: no-cache' ,
	 'x-instagram-ajax: 1' ,
	 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36' ,
	 'content-type: application/x-www-form-urlencoded' ,
	 'accept: */*' ,
	 'cache-control: no-cache' ,
	 'authority: www.instagram.com' ,
	 'referer: https://www.instagram.com/explore/tags/'+tag_name+'/', 
	 ]

	c.setopt(c.URL, 'https://www.instagram.com/query/')
	c.setopt(c.WRITEDATA, buffer)
	c.setopt(c.HTTPHEADER, header)
	c.setopt(c.POSTFIELDS, postfields)
	c.perform()
	c.close()


	body = buffer.getvalue()
	print body
	#TODO: Make Sure Response is JSON by parsing Response Type Header

	#Decompress Zipped Response
	decompressed_data=zlib.decompress(body, 16+zlib.MAX_WBITS)
	print(decompressed_data)