#!/usr/bin/env python

# Importing the controllers that will handle
# the generation of the pages:
from controllers import crons,ajax,generate,mainh

# Importing some of Google's AppEngine modules:
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

# This is the main method that maps the URLs
# of your application with controller classes.
# If a URL is requested that is not listed here,
# a 404 error is displayed.
import webapp2
from controllers import mainh,storage

def main():
  app = webapp2.WSGIApplication([
                                ('/', interface.Overview),
                                ('/api/datastore',storage.StoreHandler)
                                ],debug=True)


if __name__ == '__main__':
	main()
