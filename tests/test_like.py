import os
import sys
import leaderboard
import unittest
import random
from flask import json, jsonify


class LeaderboardTestCase(unittest.TestCase):

	JSON 		= 'application/json'
	LIKE_API 	 = 'api/images/like'
	UNLIKE_API   = 'api/images/unlike'
	LEADERBOARD_API = 'api/images/leaderboard'


	def setUp(self):
		self.app = leaderboard.app.test_client()
		assert self.app != None
		#self.app.config['TESTING'] = True
		leaderboard.init_db()
	

	# test liking an image multiple times
	# check that response is appropiate count
	def test_like_multiple_like(self):
		image_id = random.randint(1, sys.maxint)
		mydata = json.dumps({'image':image_id, 'user':'123456'})
		count = 300
		for x in range (0, count):
			resp = self.app.post(self.LIKE_API, 
				data = mydata, 
				content_type = self.JSON)
		jdata = json.loads(resp.data)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(jdata['image_count'], count)


	## simple test for like 
	def test_like(self):
		mydata = json.dumps({'image':'123444', 'user':'2345666'})
		resp = self.app.post(self.LIKE_API, 
			data = mydata, 
			content_type = self.JSON)
		self.assertEqual(resp.status_code, 200)


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
