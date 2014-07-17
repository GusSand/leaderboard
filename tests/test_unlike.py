import unittest
import os
import sys
import leaderboard
from flask import json, jsonify
import random


# tests needed for like:
	# 1. bad params
	# 2. image id not in the collection
	# 3. remove from the db
	# 4. decrease count

class UnlikeTestCase(unittest.TestCase):

	JSON 		= 'application/json'
	LIKE_API 	 = 'api/images/like'
	UNLIKE_API   = 'api/images/unlike'


	def setUp(self):
		self.app = leaderboard.app.test_client()
		#print 'done with setup'
		assert (self.app != None)
		leaderboard.init_db()


	#	Test for an image that exists and has 
	#   more than one like
	def test_unlike_decrease_count(self):

		# first like the image multiple times
		image_id = random.randint(1, sys.maxint)
		mydata = json.dumps({'image':image_id, 'user':'123456'})
		
		for x in range (0, 3):
			resp = self.app.post(self.LIKE_API, 
				data = mydata, 
				content_type = self.JSON)

		#print str(resp.data)
		jdata = json.loads(resp.data)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(jdata['image_count'], 3)


		# now unlike once and make sure it's only two
		unlikedata = json.dumps({'image':image_id, 'user':'5678'})
		resp = self.app.post(self.UNLIKE_API, 
			data = unlikedata, 
			content_type = self.JSON)

		self.assertEqual(resp.status_code, 200)
		#print str(resp.data)
		jdata = json.loads(resp.data)
		self.assertEqual(jdata['image_count'], 2)


	# Test the case where there is only one like
	# so we would need to remove from the db. 
	# to test this case we are gonna like
	# an image once and then unlike it right 
	# away. to assure there is no collisions
	# we will use a random imageid
	def test_unlike_remove_from_db(self):
		
		# first like the image and make sure its only once
		image_id = random.randint(1, sys.maxint)
		mydata = json.dumps({'image':image_id, 'user':'5678'})
		likeresp = self.app.post(self.LIKE_API, 
			data = mydata, 
			content_type = self.JSON)
		self.assertEqual(likeresp.status_code, 200)
		jdata = json.loads(likeresp.data)
		self.assertEqual(jdata['image_count'], 1)

		# now finally unlike
		unlikedata = json.dumps({'image':image_id, 'user':'5678'})
		resp = self.app.post(self.UNLIKE_API, 
			data = unlikedata, 
			content_type = self.JSON)

		self.assertEqual(resp.status_code, 200)
		#print str(resp.data)
		jdata = json.loads(resp.data)
		self.assertEqual(jdata['image_count'], 0)


	# Test for unliking an image that doesn't exist.
	# return 304 which is unmodified so that the
	# API caller knows. 
	def test_unlike_invalid_image(self):
		mydata = json.dumps({'image':0, 'user':'123456'})
		resp = self.app.post(self.UNLIKE_API, 
			data = mydata, 
			content_type = self.JSON)
		self.assertEqual(resp.status_code, 304)


	# Response should return a 400 since we are not 
	# passing any json
	def test_unlike_invalid_payload(self):
		resp = self.app.post(self.UNLIKE_API)
		assert 'invalid payload' in resp.data
		self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
	unittest.main(verbosity =2)