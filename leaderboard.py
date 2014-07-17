
"""
    Leaderboard Service
    ~~~~~~~~~~~~~~~~~~~


	A service that will return the statistics on which objects are the most liked
	in our community. 
	The service provides APIs for Like and unlike. 

	Most importantly the service provides an API for that will  provide a means of querying 
	for ranked list of the top K
	images that have received the most likes in the following time periods: 
	last 24 hours, => day
	36 hours,  => 3rd day
	1 week, => week
	1 month, => month
	1 year.=> year. 


	Base URL: 
		TODO: 


	usage: 
	API Expects:


	returns:

    200 - successful submission
	400 - Bad request 
	500 - Server error


	:copyright: (c) 2014 by Gustavo Sandoval.

"""
import os
import pymongo
from flask import Flask, request, session, g, abort, make_response, Response, json, jsonify
from urlparse import urlparse
import datetime
from datetime import timedelta


# the main app. 
# comment or uncomment the debug = true for getting debug logging
# while running on local host of the unit tests. 
app = Flask(__name__)
#app.debug = True



###############################################################
#
#	Database stuff
#
###############################################################


##
## Opens a new db connection if there's none for the current app context
## 
def get_db():
	#app.logger.debug('Entered: get_db' )
	if not hasattr(g, 'mongo_db'):
		g.mongo_db = init_db()
	return g.mongo_db

##
## Connects to the actual db
## First tries the one in heroku then localhost
def init_db():
	#app.logger.debug('Entered: init_db' )
	mongo_url = os.environ.get('MONGOHQ_URL')
	if mongo_url:
		conn = pymongo.Connection(mongo_url)
		# app.logger.debug('got heroku connection to mongo' )
		db = conn[urlparse(mongo_url).path[1:]]
	else:
		conn = pymongo.Connection('localhost', 27017)
		# app.logger.debug('got localhost connection to mongo' )	
		db = conn['leaderboard-db3']
	return db


###############################################################
#
#	Routes
#
###############################################################


@app.errorhandler(400)
def server_error():
	return make_response(standard_response(None, 400, 'Sorry an Error Ocurred'), 400)


###
###	Create or liking an Image
### 
@app.route("/api/images/like", methods=['POST'])
def images_like():
	
	app.logger.debug('Entered images_like. Payload: ' )
	json = request.get_json()

	app.logger.debug("json:")
	app.logger.debug(json)

	# First validate all the payload & params
	if (json == None):
		return Response(status=400, response='invalid payload')
	image = json.get('image')	
	if (image == None):
		return Response(status=400, response='invalid image id')
	user  = request.get_json().get('user')
	if (user == None):
		return Response(status=400, response='invalid user id')

	#everything ok, let's do work
	db = get_db()
	likes = db['likes']
	count = 1

	# check to see if this exists in the db and how many likes it has
	key = likes.find_one( { "image_id" : image} )

	if (key is None):
		# first time seen
		app.logger.debug('inserting new entry in db' )

		like = {
			'image_id' : image, 
			'user_id' : user, 
			'date_list' : [datetime.datetime.utcnow()],
			'count' : count	
		}	

		# since first time seen, we insert in the db
		like_id = likes.insert(like)
		app.logger.debug('inserted in db' )

	else:
		# we have seen this image id before
		app.logger.debug('updating in db' )
		app.logger.debug(key)

		count = key['count']
		count = count + 1

		# add at the end of the list of dates
		datelist = key['date_list']
		datelist.append(datetime.datetime.utcnow())

		# update the entry in the db
		like_id = likes.update(
				{ 	'image_id' : image, }, 
				{
					'image_id' : image, 
					'user_id'  : user, 
					'date_list' : datelist,
					'count' : count					
				}, 
			)

		app.logger.debug('updated in db' )


	resp = jsonify(image_id=image, image_count=count)
	return resp


	
###
###	Unliking an Image
### 
@app.route("/api/images/unlike", methods=['POST'])
def images_unlike():
	app.logger.debug('Entered images_unlike. Payload: ' )
	json = request.get_json()
	app.logger.debug("json:")
	app.logger.debug(json)

	# First validate all the payload & params
	if (json == None):
		return Response(status=400, response='invalid payload')
	image = json.get('image')	
	if (image == None):
		return Response(status=400, response='invalid image id')
	user  = request.get_json().get('user')
	if (user == None):
		return Response(status=400, response='invalid user id')


	#everything ok, let's do work
	db = get_db()
	likes = db['likes']

	# check to see if this exists in the db if it doesn't 
	# we will return HTTP 304 not modified
	key = likes.find_one( { "image_id" : image} )
	if (key is None):
		error = 'not modified'
		return Response(status=304, response=error)

	count = key['count']
	count = count - 1

	if (count == 0):
		# we need to remove the entry for the image
		app.logger.debug('removing entry for ' + str(image) )
		likes.remove({'image_id' : image})

	else:
		# we just need to decrease the likes
		app.logger.debug('decreasing the likes for ' + str(image))

		#remove the last date
		datelist = key['date_list']
		datelist.pop()

		# update in the db
		like_id = likes.update(
				{ 	'image_id' : image, }, 
				{
					'image_id' : image, 
					'user_id'  : user, 
					'date_list' : datelist,
					'count' : count					
				}, 
			)

		app.logger.debug('updated in db' )


	resp = jsonify(image_id=image, image_count=count)
	return resp



###
###	Route for getting the leaderboard or statistics for images
### The API should provide a means of querying for ranked list of the top
### K images that have received the most likes in the following time periods: 
### last 24 hours, 36 hours, 1 week, 1 month, and 1 year.
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
###
###
###	

@app.route("/api/images/leaderboard", methods=['GET'])
def images_leaderboard():
	app.logger.debug('Entered images_leaderboard. Payload: ' )

	args = request.args.to_dict()
	app.logger.debug(args)
	
	# First validate all the payload & params
	if (len(args) == 0):
		return Response(status=400, response='invalid payload')

	period = args.get('period', '')
	if (period == None or period not in ['24hrs', '36hrs', 'week', 'month', 'year']):
		return Response(status=400, response='invalid period. Valid are 24hrs, 36hrs, week, month, year')

	k = args.get('k', '')
	try:
		n = int(k)
		if (n == None or n < 0 or n > 100):
			raise Exception()
	except Exception, e:
		return Response(status=400, response=k + 'is an invalid count. Max is 100')
	
	# Everything ok, let's do some work
	db = get_db()

	# here we compute the appropiate period and ask from the database for the top likes in the daterange required
	targetdate = datetime.datetime.utcnow() - gettimedelta(period)
	cursor_likes = db.likes.find({"date_list" : {"$lt": targetdate}}).sort('count', pymongo.DESCENDING).limit(n)
	#app.logger.debug("like_list")
	likes = []
	for doc in cursor_likes :
		#app.logger.debug(doc)
		like = { 'image_id':doc['image_id'], 'count': doc['count'] }
		#app.logger.debug(like)
		likes.append(like)

	resp = jsonify(likes=likes)
	app.logger.debug("response: " + resp.data)
	return resp


##
## Helper function to figure out the time based on 
## on the period passed to the leaderboard function. 
## At this point it should be a valid period since it has been checked
def gettimedelta(period):
#24hrs, 36hrs, week, month, year'
	if (period == '24hrs'):
		return timedelta(days=1)
	elif (period == '36hrs'): 
		return timedelta(days=1, hours =12)
	elif (period == 'week'):
		return timedelta(days=7)
	elif (period == 'month'):
		return timedelta(days=30)
	elif (period == 'year'):
		return timedelta(days=365)

###
### Root Route, doesn't do anything. just make sure we are loaded
###
@app.route('/')
def hello():
	return 'Please use the API'


##
## So that we can run it in the localhost
if __name__ == '__main__':
	#app.run(debug=True)
	app.run()