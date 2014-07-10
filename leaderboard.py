
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



app = Flask(__name__)
app.debug = True





###############################################################
#
#	Database stuff
#
###############################################################


##
## Opens a new db connection if there's none for the current app context
## 
def get_db():
	app.logger.debug('Entered: get_db' )
	if not hasattr(g, 'mongo_db'):
		g.mongo_db = init_db()
	return g.mongo_db

##
## Connects to the actual db
##
def init_db():
	app.logger.debug('Entered: init_db' )
	mongo_url = os.environ.get('MONGOHQ_URL')


	if mongo_url:
		# first try to see if we are running under heroku
		conn = pymongo.Connection(mongo_url)
		app.logger.debug('got heroku connection to mongo' )
		db = conn[urlparse(mongo_url).path[1:]]

	else:
		# not on an app with MongoHQ, try localhost
		conn = pymongo.Connection('localhost', 27017)
		app.logger.debug('got localhost connection to mongo' )	
		db = conn['leaderboard-db3']


	return db

# TODO: teardown connections
#@app.teardown_appcontext
#def close_db(error):
#	if hasattr(g, 'mongo_db'):
		#g.mongo_db.close()


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
	
	error = None
	app.logger.debug('Entered images_like. Payload: ' )
	json = request.get_json()

	app.logger.debug("json:")
	app.logger.debug(json)

	# First validate all the payload
	if (json == None):
		error = 'invalid payload'
		return Response(status=400, response=error)

	image = json.get('image')	
	if (image == None):
		error = 'invalid image id'
		return Response(status=400, response=error)

	user  = request.get_json().get('user')
	if (user == None):
		error == 'invalid user id'
		return Response(status=400, response=error)


	#everything ok, let's do work
	
	db = get_db()
	likes = db['likes']
	count = 1

	# check to see if this exists in the db and how many likes it has
	#key = likes.find_one( { "image_id" : image, likes.count: { '$exists': True }})
	#TODO
	key = likes.find_one( { "image_id" : image} )


	if (key is None):

		app.logger.debug('inserting new entry in db' )

		like = {
			'image_id' : image, 
			'user_id' : user, 
			'date_list' : [datetime.datetime.utcnow()],
			'count' : count	
		}	
		like_id = likes.insert(like)
		app.logger.debug('inserted in db' )

	else:

		app.logger.debug('updating in db' )
		app.logger.debug(key)

		count = key['count']
		count = count + 1

		# TODO: 
		# try:			
		# except:			
		# 	

		# try:
		# except:
		# 	datelist = [datetime.datetime.utcnow()]

		datelist = key['date_list']
		datelist.append(datetime.datetime.utcnow())

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
###	Route Unliking an Image
### 
@app.route("/api/images/leaderboard", methods=['GET'])
def images_leaderboard():
	app.logger.debug('Entered images_leaderboard. Payload: ' )
	app.logger.debug(request.get_json())

	try:
		
		db = get_db()
		likes = db.likes.find_one()

		#data = db.collection_names()
		#app.logger.debug(data)

		return str(likes) #jsonify(username=g.user.username)


	except:
		app.logger.debug('Server Error' )
		abort(400)


###
###	Destroy or Unliking an Image
### 
@app.route("/api/images/unlike", methods=['POST'])
def images_unlike():
	app.logger.debug('Entered images_unlike. Payload: ' )
	app.logger.debug(request.get_json())

	try:


		return 'ok'


	except:
		app.logger.debug('Server Error' )
		abort(500)





###
### Root Route, doesn't do anything. just make sure we are loaded
###
@app.route('/')
def hello():
	return 'Please use the API'


##
## So that we can run it in the localhost
if __name__ == '__main__':
	app.run(debug=True)
	#app.run()