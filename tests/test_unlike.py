import unittest
import os
import leaderboard
from flask import json, jsonify

class UnlikeTestCase(unittest.TestCase):

	JSON 		= 'application/json'
	LIKE_API 	 = 'api/images/like'
	UNLIKE_API   = 'api/images/unlike'


	def setUp(self):
		self.app = leaderboard.app.test_client()
		#print 'done with setup'
		assert (self.app != None)
		leaderboard.init_db()


# tests needed for like:
	# 1. bad params
	# 2. image id not in the collection
	# 3. remove from the db
	# 4. decrease count

	#def test_unlike_decrease_count(self):



	def test_unlike_invalid_image(self):
		
		mydata = json.dumps({'image':0, 'user':'123456'})

		resp = self.app.post(self.UNLIKE_API, 
			data = mydata, 
			content_type = self.JSON)

		#print str(resp.data)
		self.assertEqual(resp.status_code, 304)



	def test_unlike_invalid_payload(self):
		resp = self.app.post(self.UNLIKE_API)
	
		# Response should return a 400 since we are not 
		# passing any json
		#print ('Error: ' + str(resp.data))
		assert 'invalid payload' in resp.data
		self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
	unittest.main(verbosity =2)