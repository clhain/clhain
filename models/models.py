#!/usr/bin/env python

from google.appengine.ext import db

# These classes define the data objects
# that you will be able to store in
# AppEngine's data store.

class Ping(db.Model):
	responseTime = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now_add=True)

class Day(db.Model):
	averageResponseTime = db.IntegerProperty()
	totalPings = db.IntegerProperty()
	date = db.DateProperty(auto_now_add=True)
	
class DownTime(db.Model):
	date = db.DateTimeProperty(auto_now_add=True)