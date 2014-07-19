import unittest
import os
import sys
import leaderboard
import random
from flask import json, jsonify
import datetime
from datetime import timedelta

class LeaderboardTestCase(unittest.TestCase):

	JSON 		= 'application/json'
	LIKE_API 	 = 'api/images/like'
	UNLIKE_API   = 'api/images/unlike'
	LEADERBOARD_API = 'api/images/leaderboard'
	db = None


	def setUp(self):
		self.app = leaderboard.app.test_client()
		assert self.app != None
		#self.app.config['TESTING'] = True
		self.db = leaderboard.init_db()

	# Gonna create a set of 10, 5 and 3 likes for diff images for 
	# use in our tests
	def like_images(self, targetdate):
		ids = ['123', '1234', '12345']
		counts = [10, 5, 3]
		for x in range (0, len(ids)):
			like = {'image_id': ids[x], 'user_id':ids[x], 'date_list':[targetdate], 'count':counts[x]}
			self.db.likes.insert(like)

	# remove from the db all the images added in like_images
	def remove_images(self):
		ids = ['123', '1234', '12345']
		for id in ids:
			self.db.likes.remove({'image_id':id})



	# the interesting test case:
	# image has a bunch of likes but only 1 in our period
	def test_like_dates_1(self):
		targetdate = datetime.datetime.utcnow() - timedelta(hours=23)
		self.like_images(targetdate)

		otherdate = datetime.datetime.utcnow() - timedelta(hours=25)
		dateList = [otherdate, otherdate, otherdate, otherdate, otherdate, targetdate]

		like = {'image_id':'5678', 'user_id':'5678', 'date_list':dateList, 'count':len(dateList)}
		self.db.likes.insert(like)

		resp = self.app.get('api/images/leaderboard?period=24hrs&k=10')
		self.assertEqual(resp.status_code, 200)
		jdata = json.loads(resp.data)
		self.assertTrue(jdata['likes'] >= 4)
		self.assertEqual(jdata['likes'][3]['count'], 1)

		self.db.likes.remove({'image_id':'5678'})
		self.remove_images()

	# here a test where we add images for a year
	# and request for a month. Should be 0
	def test_no_likes_in_period(self):
		targetdate = datetime.datetime.utcnow() - timedelta(days=360)
		self.like_images(targetdate)	

		# get the data for the past month
		resp = self.app.get('api/images/leaderboard?period=month&k=10')
		self.assertEqual(resp.status_code, 200)
		jdata = json.loads(resp.data)

		# we know there should be at least 3
		self.assertTrue(len(jdata['likes']) == 0)

		# remove test data
		self.remove_images()


	# test for images liked in the past week 
	def test_get_top_k_likes_for_a_year(self):
		# our target date should be a little less than 24 hours
		targetdate = datetime.datetime.utcnow() - timedelta(days=360)
		self.like_images(targetdate)	

		# get the data for the past 24 hrs
		resp = self.app.get('api/images/leaderboard?period=year&k=10')
		self.assertEqual(resp.status_code, 200)
		jdata = json.loads(resp.data)

		# we know there should be at least 3
		self.assertTrue(len(jdata['likes']) >=3)

		# remove test data
		self.remove_images()



	# test for images liked in the past month 
	def test_get_top_k_likes_for_a_month(self):
		# our target date should be a little less than 24 hours
		targetdate = datetime.datetime.utcnow() - timedelta(days=29)
		self.like_images(targetdate)	

		# get the data for the past 24 hrs
		resp = self.app.get('api/images/leaderboard?period=month&k=10')
		self.assertEqual(resp.status_code, 200)
		jdata = json.loads(resp.data)

		# we know there should be at least 3
		self.assertTrue(len(jdata['likes']) >=3)

		# remove test data
		self.remove_images()


	# test for images liked in the past week 
	def test_get_top_k_likes_for_a_week(self):
		# our target date should be a little less than 24 hours
		targetdate = datetime.datetime.utcnow() - timedelta(days=6)
		self.like_images(targetdate)	

		# get the data for the past 24 hrs
		resp = self.app.get('api/images/leaderboard?period=week&k=10')
		self.assertEqual(resp.status_code, 200)
		jdata = json.loads(resp.data)

		# we know there should be at least 3
		self.assertTrue(len(jdata['likes']) >=3)

		# remove test data
		self.remove_images()



	# test for images liked in the past 36 hrs. 
	def test_get_top_k_likes_for_36_hrs(self):
		# our target date should be a little less than 24 hours
		targetdate = datetime.datetime.utcnow() - timedelta(hours=35)
		self.like_images(targetdate)	

		# get the data for the past 24 hrs
		resp = self.app.get('api/images/leaderboard?period=36hrs&k=10')
		self.assertEqual(resp.status_code, 200)
		jdata = json.loads(resp.data)

		# we know there should be at least 3
		self.assertTrue(len(jdata['likes']) >=3)

		# remove test data
		self.remove_images()


	# test for images liked in the past 24 hrs. 
	def test_get_top_k_likes_for_24_hrs(self):
		# our target date should be a little less than 24 hours
		targetdate = datetime.datetime.utcnow() - timedelta(hours=23)
		self.like_images(targetdate)	

		# get the data for the past 24 hrs
		resp = self.app.get('api/images/leaderboard?period=24hrs&k=10')
		self.assertEqual(resp.status_code, 200)
		jdata = json.loads(resp.data)

		# we know there should be at least 3
		self.assertTrue(len(jdata['likes']) >=3)

		# remove test data
		self.remove_images()

	
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

