# Copyright 2015 Daniel Neve
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#System imports
import logging

#Library imports
import requests

#Google Imports
from google.appengine.ext.webapp import template

#Project imports
import common.base
import secrets.facebook
import defines
import storage

def NetGetRealTimeSubscriptions():
	url = "https://graph.facebook.com/" + defines.PLATFORM_VERSION + "/" + str( secrets.facebook.CLIENT_ID ) + "/subscriptions"
	
	payload = \
	{
		'access_token' : secrets.facebook.ACCESS_TOKEN
	}
	
	response = requests.get( url = url, params = payload )
	return ( response.status_code, response.json() )

class Handler( common.base.Handler ):
	def Main( self, params ):
		logging.debug( "Facebook Admin Main()" )
		
		# Get list of subscribed urls from facebook
		subscriptions = NetGetRealTimeSubscriptions()[ 1 ]
		
		# Construct the URL that will allow us to subscribe us with our current URL
		subscribeUrl = self.app.router.build \
		(
			self.request,
			"admin_branch",
			(),
			{
				'handler' : "facebook",
				'branch' : "subscribe",
				'_full' : False,
				'_scheme' : "https"
			}
		)
		
		
		# Construct the URL that will allow us to subscribe us with our current URL
		unsubscribeUrl = self.app.router.build \
		(
			self.request,
			"admin_branch",
			(),
			{
				'handler'	: "facebook",
				'branch' 	: "unsubscribe",
				'_full' 	: False,
				'_scheme' 	: "https"
			}
		)
		
		for subscription in subscriptions[ 'data' ]:
			subscription[ "unsubscribe" ] = { "url" : unsubscribeUrl }
		
		path = "templates/admin/facebook.html"
		values = \
		{
			"subscriptions" : subscriptions[ 'data' ],
			"subscribe" :
			{
				"url" : subscribeUrl
			}
		}
		
		if len( subscriptions[ 'data' ] ) == 1:
			values[ "pageonly" ] = True
		
		self.response.data = template.render( path, values )
	
	def Subscribe( self, params ):
		logging.debug( "Facebook Subscribe()" )
		
		if 'object' not in self.request.POST:
			self.response.status = requests.codes.bad_request
			logging.error( "Missing object parameter" )
			return
			
		if 'field' not in self.request.POST:
			self.response.status = requests.codes.bad_request
			logging.error( "Missing field parameter" )
			return
			
		callbackUrl = self.app.router.build \
		(
			self.request,
			"callback",
			(),
			{
				'version' : 1,
				'handler' : "facebook",
				'_full' : True,
				'_scheme' : "https"
			}
		)
		
		logging.debug( "callback url: " + callbackUrl )
		
		import random
		import string
		authToken = ''.join( random.SystemRandom().choice( string.ascii_uppercase + string.digits ) for _ in range( 10 ) )
		
		tokenStorage = storage.CreateTemporaryAuthToken( defines.SUBSCRIBE_HANDSHAKE_TOKEN, authToken )
		tokenStorage.put()
		
		payload = \
		{
			'object' : self.request.POST[ 'object' ],
			'fields' : self.request.POST[ 'field' ],
			'callback_url' : callbackUrl,
			'verify_token' : authToken,
			'access_token' : secrets.facebook.ACCESS_TOKEN
		}
		
		url = "https://graph.facebook.com/" + defines.PLATFORM_VERSION + "/" + str( secrets.facebook.CLIENT_ID ) + "/subscriptions"
		
		response = requests.post( url, params = payload )
		
		self.ReturnToMain( response )
	
	def Unsubscribe( self, params ):
		logging.debug( "Facebook Unsubscribe()" )
		
		if 'object' not in self.request.POST:
			self.response.status = requests.codes.bad_request
			logging.error( "Missing object parameter" )
			return
		
		payload = \
		{
			'object' : self.request.POST[ 'object' ],
			'access_token' : secrets.facebook.ACCESS_TOKEN
		}
		
		if 'field' in self.request.POST:
			payload[ 'fields' ] = self.request.POST[ 'field' ]
		
		url = "https://graph.facebook.com/" + defines.PLATFORM_VERSION + "/" + str( secrets.facebook.CLIENT_ID ) + "/subscriptions"
		
		response = requests.delete( url, params = payload )
		
		logging.debug( "URL: " + response.url )
		
		self.ReturnToMain( response )
		
	def ReturnToMain( self, response ):
		
		# Construct the URL to the facebook admin page
		redirectUrl = self.app.router.build \
		(
			self.request,
			"admin_handler",
			(),
			{
				'handler' : "facebook",
				'_full' : False,
				'_scheme' : "https"
			}
		)
		
		path = "templates/admin/facebook_feedback.html"
		values = \
		{
			"redirect" : response.status_code == requests.codes.ok,
			"redirectUrl" : redirectUrl,
			"feedback" : response.text
		}
		
		self.response.data = template.render( path, values )
		self.response.status = response.status_code
	
	def List( self ):
		logging.debug( "Facebook Admin List()" )
		
		response = NetGetRealTimeSubscriptions()
		
		self.response.status = response[ 0 ]
		self.response.data = str( response[ 1 ] )