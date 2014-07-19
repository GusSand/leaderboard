import unittest
import os
import sys
import leaderboard
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


	#tests:
	# 3. day, 
	# 4. dayhalf
	# 5. week
	# 6. month
	# 7. year


	def test_get_top_k_likes(self):
		resp = self.app.get('api/images/leaderboard?period=year&k=10')
		self.assertEqual(resp.status_code, 200)
		#jdata = json.loads(resp.data)
		#self.assertEqual(jdata[''])


	# test for passing an invalid count. Valid is up to 1000
	# Expect 400. 
	def test_leaderboard_invalid_count(self):
		resp = self.app.get('api/images/leaderboard?period=year&k=101')
		assert 'invalid count' in resp.data
		self.assertEqual(resp.status_code, 400)


	# test for passing an invalid period 
	# allowed are: ['24hrs', '36hrs', 'week', 'month', 'year']
	# Expect 400. 
	def test_leaderboard_invalid_period(self):
		resp = self.app.get('api/images/leaderboard?period=days')
		assert 'invalid period' in resp.data
		self.assertEqual(resp.status_code, 400)


	# Test when invalid payload.
	# Expect 400. 
	def test_leaderboard_invalid_payload(self):
		resp = self.app.get('api/images/leaderboard')
		assert 'invalid payload' in resp.data
		self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
	unittest.main(verbosity =1)

