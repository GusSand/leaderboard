
   Leaderboard Service
    ~~~~~~~~~~~~~~~~~~~


	A service that will return the statistics on which objects are the most liked
	in a community. 
	The service provides APIs for Like and unlike. 

	Most importantly the service provides an API for that will  provide a means of querying 
	for ranked list of the top K images that have received the most likes in the following time periods: 24hrs, 36hrs, 
	1 week, 1 month and 1 year. 
	
  The service currently runs in Heroku:
  
  
	Base URL: 
		http://imageleaderboard.herokuapp.com/api/images/ 


LIKE:
### Supports: POST
### Expects: json with image and user.
### Returns: image_id and count. HTTP 200 or 400
###
### Format for call: api/images/like
### body: {image:'imageid', user:'userid'}
### 
### Using Curl: 
### curl -d '{"user":"123", "image":"123"}' http://imageleaderboard.herokuapp.com/api/images/like --header "Content-Type:application/json"
###

UNLIKE:
###
###	Unliking an Image
### Supports: POST
### Expects: json with image and user. 
### Returns: image_id and count. HTTP 200, 400 or 304 if not found
###
### Format for call: api/images/unlike
### body: {image:'imageid', user:'userid'}
###
### Where: 
### - period must be one of: '24hrs', '36hrs', 'week', 'month', 'year'
### - k must be between 0 and 100
###
### Using Curl: 
### curl -d '{"user":"123", "image":"123"}' http://imageleaderboard.herokuapp.com/api/images/unlike --header "Content-Type:application/json"
###


LEADERBOARD:
### Supports: GET
### Expects: json with
###	Route for getting the leaderboard or statistics for images
### The API provides means for querying for a ranked list of the top
### K images that have received the most likes in the following time periods: 
### last 24 hours, 36 hours, 1 week, 1 month, and 1 year.
###
### Format for call: http://imageleaderboard.herokuapp.com/api/images/leaderboard?period=24hrs&k=10
###
### Where: 
### - period must be one of: '24hrs', '36hrs', 'week', 'month', 'year'
### - k must be between 0 and 100
### 
### response:
#   {
#    "likes": [ 
#	 	{
# 			"image_id": "12", 
# 			"count"	  : 100
# 		}, 
# 		{
# 			"image_id": "1234", 
# 			"count"   : 12
# 		}
# 	  ] 
# 	}

	
For more info look at leaderboard.py


Implementation notes:
=====================

In order to run this in your machine you will need to install mongodb. As this used for storage. 
The best way to do this is using using brew on your Mac. http://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x/

You will also need to install flask which is the python microframework I used for implementing the REST service. 
The best way is to just use PIP install flask

The code includes a full set of unit Tests using Python's unittest framework. 
The best way to run them is using nose:
Nosetests -v




