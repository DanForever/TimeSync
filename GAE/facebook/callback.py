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

from json import loads as stringToJson

#Library imports
import requests

#Project imports
import common.base
import secrets.facebook
import storage
import defines
import events

class Handler( common.base.Handler ):
	def Get( self ):
		logging.debug( "Facebook callback handler Get(): " + str( self.request.GET ) )

		if not ( self.request.GET[ 'hub.mode' ] == "subscribe" ):
			logging.debug( "Facebook callback handler Get(): Missing subcribe mode" )
			self.response.status = requests.codes.bad_request
			return
		
		if 'hub.verify_token' not in self.request.GET:
			logging.debug( "Facebook callback handler Get(): Missing verify_token" )
			self.response.status = requests.codes.bad_request
			return
		
		storedToken = storage.FindTemporaryAuthToken( self.request.GET[ 'hub.verify_token' ] )
		
		if not storedToken:
			logging.debug( "Facebook Missing storage token" )
			self.response.status = requests.codes.unauthorized
			return
		
		token = storedToken.token
		storedToken.delete()
		
		if token == defines.SUBSCRIBE_HANDSHAKE_TOKEN:
			self.response.status = requests.codes.ok
			self.response.data = self.request.GET[ 'hub.challenge' ]
		else:
			logging.debug( "Facebook callback handler Get(): Retrieved token does not match expected token" )
			self.response.status = requests.codes.unauthorized
	
	def Post( self, params ):
		logging.debug( "CallbackHandler Post()" )
		logging.debug( "Callback headers: " + str( self.request.headers ) )
		logging.debug( "Callback POST: " + str( self.request.POST ) )
		logging.debug( "Callback body: " + str( self.request.body ) )
		
		# First authenticate that the request was made by facebook
		import hmac
		import hashlib
		
		calculatedSha = "sha1=" + hmac.new( secrets.facebook.APP_SECRET, str( self.request.body ), hashlib.sha1 ).hexdigest()
		receivedSha = self.request.headers[ 'X-Hub-Signature' ]
		
		if calculatedSha == receivedSha:
			logging.debug( "Calculated SHA (" + calculatedSha + ") matches received SHA" )
			
			requestData = stringToJson( self.request.body )
			
			if requestData[ 'object' ] == "user":
				for entry in requestData[ 'entry' ]:
					if "events" in entry[ 'changed_fields' ]:
						fbuid = entry[ 'uid' ]
						
						logging.debug( "Checking subscription data for user: " + str( fbuid ) )
						fbSub = storage.FindFacebookSubscription( fbuid )
						
						if fbSub.events:
							logging.debug( "Updating events for user: " + str( fbuid ) )
							
							db = self.CreateConfigDB( defines.PLATFORM, fbSub.watchToken )
							
							events.Fetch( fbSub.watchToken, db, fbuid )
			
			self.response.status = requests.codes.ok
		
		else:
			self.response.status = requests.codes.unauthorized