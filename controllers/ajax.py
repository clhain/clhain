#!/usr/bin/env python

# Including the models:
from models.models import *

# We are using django's simplejson
# module to format JSON strings:
from django.utils import simplejson

from datetime import datetime,timedelta
from google.appengine.ext import webapp, db
from google.appengine.api import memcache

# The AJAX controllers:

class TwentyFourHours(webapp.RequestHandler):
	def get(self):
	
		# This class selects the response times
		# for the last 24 hours.
	
		# Checking whether the result of this
		# function is already cached in memcache:
		jsonStr = memcache.get("TwentyFourHoursCache")
		
		# If it is not, we need to generate it:
		if jsonStr is None:

			query = db.GqlQuery("SELECT * FROM Ping WHERE date>:dt ORDER BY date",
						dt=(datetime.now() - timedelta(hours = 24)))
			
			results = query.fetch(limit=300)
			chart = []
			for Ping in results:
				chart.append({
					"label": Ping.date.strftime("%H:%M"),
					"value": Ping.responseTime
				})
			
			jsonStr = simplejson.dumps({
				"chart"		: {
					# tooltip is used by the jQuery chart:
					"tooltip"	: "Response time at %1: %2ms",
					"data"		: chart
				},
				"downtime"	: getDowntime(1)
			})
			
			# Caching it for five minutes:
			memcache.add("TwentyFourHoursCache", jsonStr, 300)
		
		self.response.out.write(jsonStr);

class SevenDays(webapp.RequestHandler):
	days = 7
	def get(self):
	
		# Selecting the response times for the last seven days:
		query = db.GqlQuery("SELECT * FROM Day WHERE date>:dt ORDER BY date",
				dt=(datetime.now() - timedelta(days = self.days)))
		
		results = query.fetch(limit=self.days)
		chart = []
		for Day in results:
			chart.append({
				"label": Day.date.strftime("%b, %d"),
				"value": Day.averageResponseTime
			})
		
		self.response.out.write(simplejson.dumps({
			"chart"		: {
				"tooltip"	: "Average response time for %1: %2ms",
				"data"		: chart
			},
			"downtime"	: getDowntime(self.days)
		}))

# Extending the SevenDays class and only
# increasing the days member:

class ThirtyDays(SevenDays):
	days = 30

def getDowntime(days=1):

	# Checking whether the result of this function
	# already exists in memcache. Notice the key for get():
	
	downTimeList = memcache.get("DownTimeCache"+str(days))
	if downTimeList is None:

		query = db.GqlQuery("SELECT * FROM DownTime WHERE date>:dt ORDER BY date",
				dt=(datetime.now() - timedelta(days = days)))
		
		results = query.fetch(limit=100)
		
		downTimeList = []
		downTimePeriod = {}
		
		if len(results) == 0:
			return []
		
		# This loop "compacts" the downtime:
		
		for DownTime in results:
		
			if not downTimePeriod.has_key("begin"):
				downTimePeriod = {"begin":DownTime.date,"end":DownTime.date}
				continue
				
			if DownTime.date - downTimePeriod['end'] < timedelta(minutes=8):
				downTimePeriod['end'] = DownTime.date
			else:
				downTimeList.append(downTimePeriod)
				downTimePeriod = {"begin":DownTime.date,"end":DownTime.date}
		
		downTimeList.append(downTimePeriod)
		
		# Formatting the output of this function:
		
		for i in downTimeList:
			
			if i['end'] + timedelta(minutes=5) > datetime.now():
				i['period'] = timedeltaFormat(((datetime.now() - i['begin'])).seconds)
				i['end'] = "NOW"
			else:
				i['period'] = timedeltaFormat(((i['end'] - i['begin']) + timedelta(minutes=5)).seconds)
				i['end'] = (i['end']+timedelta(minutes=5)).strftime('%H:%M on %b, %d, %Y')	
			
			i['begin'] = i['begin'].strftime('%H:%M on %b, %d, %Y')
		
		# Storing the response in memcache:
		memcache.add("DownTimeCache"+str(days), downTimeList, 300)
		
	return downTimeList

# A helper function for formatting time periods.

def timedeltaFormat(seconds):
	hours, remainder = divmod(seconds, 3600)
	minutes, seconds = divmod(remainder, 60)
	
	return ('%02d:%02d:%02d' % (hours, minutes, seconds))
