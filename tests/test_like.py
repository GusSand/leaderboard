import os
import sys
import leaderboard
import unittest
import random
from flask import json, jsonify


# All the like test cases. 
# After each test leave the db in 
# in the same state as before. 
# The tearDown method will do that. 
class LikeTestCase(unittest.TestCase):

	JSON 		= 'application/json'
	LIKE_API 	 = 'api/images/like'
	UNLIKE_API   = 'api/images/unlike'
	teardown_id = None
	db = None


	def setUp(self):
		self.app = leaderboard.app.test_client()
		assert self.app != None
		#self.app.config['TESTING'] = True
		self.db = leaderboard.init_db()

	
	def tearDown(self):
	# now remove the image data 
		if (self.teardown_id != None):
			self.db.likes.remove({'image_id' : self.teardown_id})
			key = self.db.likes.find_one({'image_id': self.teardown_id})
			self.assertEqual(key, None)
			self.teardown_id = None



	# test liking an image multiple times
	# check that response is appropiate count
	def test_like_multiple_like(self):
		image_id = random.randint(1, sys.maxint)
		self.teardown_id = image_id
		mydata = json.dumps({'image':image_id, 'user':'123456'})
		count = 30
		for x in range (0, count):
			resp = self.app.post(self.LIKE_API, 
				data = mydata, 
				content_type = self.JSON)
			self.assertEqual(resp.status_code, 200)

		jdata = json.loads(resp.data)
		self.assertEqual(jdata['image_count'], count)

	



	## simple test for like 
	def test_like(self):
		image_id = '123444'
		mydata = json.dumps({'image':image_id, 'user':'2345666'})
		resp = self.app.post(self.LIKE_API, 
			data = mydata, 
			content_type = self.JSON)
		self.assertEqual(resp.status_code, 200)
		self.teardown_id = image_id


	# Test for passing invalid image id on the payload
	# Response should return a 400
	def test_like_invalid_image(self):
		mydata = json.dumps({'user':'2345'})
		resp = self.app.post(self.LIKE_API, 
			data = mydata, 
			content_type = self.JSON)
		assert 'invalid image' in resp.data
		self.assertEqual(resp.status_code, 400)


	# Test when we don't pass any params. 
	# We should pass image & user
	# Response should return a 400
	def test_like_invalid_payload(self):
		resp = self.app.post(self.LIKE_API)
		assert 'invalid payload' in resp.data
		self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
	unittest.main(verbosity =2)
