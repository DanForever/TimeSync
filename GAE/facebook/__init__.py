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
import datetime
from json import dumps as jsonToString
#from json import loads as stringToJson

#Library imports
import requests

#Project imports
import base
import storage
import logging
import defines as defines
import net as net
import events as events

class Handler( base.Handler ):
	def Process( self, branch, action ):
		branches = \
		{
			"auth" : self.GetAccess,
			"events" : self.SubscribeEvents
		}
		
		actions = \
		{
			"subscribe" : True,
			"unsubscribe" : False,
			
			# Auth Actions
			"request" : True,
			"query"	: False
		}
		
		if branch not in branches or action not in actions:
			self.response.status = requests.codes.not_found
			return
		
		pebbleToken = self.request.headers[ 'X-User-Token' ]
		
		branches[ branch ]( pebbleToken, actions[ action ] )
		
	def SubscribeEvents( self, pebbleToken, action ):
		logging.debug( "SubscribeEvents()" )
		
		# update sub data
		fbSubData = storage.FindFacebookSubscriptionByWatchToken( pebbleToken )
		fbSubData.events = action
		fbSubData.put()
		
		if action:
			# Grab all the events for the user
			events.Fetch( pebbleToken, fbSubData.key().name() )
		
		response = \
		{
			'status' : "success",
		}
		self.response.status = requests.codes.ok
		self.response.data = jsonToString( response )
		
	def DBGetExistingDeviceAuthCode( self, pebbleToken ):
		# Find an auth request for the specified pebble
		authRequest = storage.FindPlatformAuthRequest( pebbleToken, defines.PLATFORM )
		
		if authRequest is not None:
			#check to see if the request is still valid
			expired = datetime.datetime.utcnow() > authRequest.expires
			
			if expired:
				# Delete the old request
				logging.debug( "Auth Request expired (Deleting)" )
				authRequest.delete()
				authRequest = None
			else:
				logging.debug( "Auth Request found" )
		else:
			logging.debug( "Auth Request not found" )
			
		return authRequest

	def DBCreateNewDeviceAuthCode( self, pebbleToken, authRequestResponse ):
		# Convert the specified time limit into a datetime object
		expirationTime = datetime.datetime.utcnow() + datetime.timedelta( seconds = authRequestResponse[ 'expires_in' ] )
		
		# Create parent object, this does not need to be written to the
		# database as it's only purpose is to contain the pebble token
		watch = storage.CreateWatch( pebbleToken )
		
		# Create the object
		authRequest = storage.CreatePlatformAuthRequest \
		(
			watch,
			defines.PLATFORM,
			authRequestResponse[ 'code' ],
			authRequestResponse[ 'user_code' ],
			authRequestResponse[ 'verification_uri' ],
			expirationTime,
			authRequestResponse[ 'interval' ],
		)
		
		# Add it to the database
		authRequest.put()
		
		logging.debug( "Created auth request" )
		
		return authRequest
		
		
	def CheckLoginCodeStatus( self, pebbleToken, authRequest ):
		#todo: Check time since last poll?
		logging.debug( "Checking log in status with facebook" )
		loginCodeStatus = net.GetDeviceLoginCodeStatus( authRequest.auth_code )
		
		if loginCodeStatus[ 0 ] == requests.codes.ok:
			# Create parent object, this does not need to be written to the
			# database as it's only purpose is to contain the pebble token
			watch = storage.CreateWatch( pebbleToken )
			
			accessToken = loginCodeStatus[ 1 ][ 'access_token' ]
			access = storage.CreateAccess( watch, defines.PLATFORM, accessToken )
			
			# store it in the database
			access.put()
			
			# We need to store the facebook user id for when we're told about event changes
			# And also the user's name so that we can display it on the watch as evidence of a successful sign in
			getDataStatus = net.GetCurrentUserData( accessToken )
			
			if( getDataStatus[ 0 ] == requests.codes.ok ):
				
				self.response.status = requests.codes.ok
				
				response = \
				{
					'status' : "success",
					'name' : getDataStatus[ 1 ][ 'name' ]
				}
				
				newSub = storage.CreateFacebookSubscription( getDataStatus[ 1 ][ 'id' ], pebbleToken )
				newSub.put()
				
				# No longer required
				authRequest.delete()
				
			else:
				self.response.status = requests.codes.bad_request
				response = \
				{
					'status' : "failure",
					'message' : "Could not get user details",
				}
		elif loginCodeStatus[ 1 ][ 'error' ][ 'message' ] == "authorization_pending":
		
			self.response.status = requests.codes.ok
			response = \
			{
				"status" : "require_auth",
				"url" : authRequest.user_uri,
				"code" : authRequest.user_code,
				"interval" : authRequest.update_interval
			}
			
		else:
			self.response.status = requests.codes.bad_request
			
			response = \
			{
				'status' : "error",
				'message' : loginCodeStatus[ 1 ][ 'error' ][ 'message' ],
				'user_code' : authRequest.user_code
			}
		
		self.response.data = jsonToString( response )

	def CheckPlatformAccess( self, pebbleToken ):
		# Check to see if we already have facebook access
		access = storage.FindPlatformAccessCode( pebbleToken, defines.PLATFORM )
		
		if access:
		
			response = \
			{
				'status' : "success",
			}
			self.response.status = requests.codes.ok
			self.response.data = jsonToString( response )
			return True
		return False
	
	def GetAccess( self, pebbleToken, createIfRequired ):
		
		if self.CheckPlatformAccess( pebbleToken ):
			return
		
		# Check to see if we already have facebook access
		accessToken = storage.FindPlatformAccessCode( pebbleToken, defines.PLATFORM )
		
		if accessToken:
			response = \
			{
				'status' : "success",
			}
			self.response.status = requests.codes.ok
			self.response.data = jsonToString( response )
			return
		
		# No access code yet, perhaps we've already got an existing auth request on the go?
		authRequest = self.DBGetExistingDeviceAuthCode( pebbleToken )
		
		if authRequest is None and createIfRequired:
			# No existing auth request found for this watch
			logging.debug( "Creating new auth request" )
			
			# Request new code from facebook
			authRequestResponse = net.GetNewDeviceLoginCode()[ 1 ]
			
			# Store new request
			authRequest = self.DBCreateNewDeviceAuthCode( pebbleToken, authRequestResponse )
		elif authRequest:
			# Check status
			self.CheckLoginCodeStatus( pebbleToken, authRequest )
			return
		
		if authRequest:
			logging.debug( "Turning auth request into json response" )
			
			returnData = \
			{
				"status" : "require_auth",
				"url" : authRequest.user_uri,
				"code" : authRequest.user_code,
				"interval" : authRequest.update_interval
			}
			
			self.response.status = requests.codes.ok
			self.response.data = jsonToString( returnData )
			
		else:
			logging.debug( "No auth request - creating json error response" )
			
			returnData = \
			{
				"status" : "no_auth",
				"error" : "No authorisation code found"
			}
			
			self.response.status = requests.codes.bad_request
			self.response.data = jsonToString( returnData )
