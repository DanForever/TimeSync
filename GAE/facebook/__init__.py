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

#Library imports
from requests import codes

#Project imports
import common.base
import storage
import logging
import events
import defines
import net


class Handler( common.base.Handler ):
	def GetOrCreateSubscription( self, pebbleToken, db = None ):
		fbSubData = storage.FindFacebookSubscriptionByWatchToken( pebbleToken )
		
		if fbSubData is None:
			if db is None:
				db = self.CreateConfigDB( defines.PLATFORM )
				if db is None:
					logging.warning( "No facebook access token assocated with pebble token: " + str( pebbleToken ) )
					return ( None, None )
			
			import config.user
			
			response = net.MakeRequest( config.user.USER, db )
			
			if response[ 0 ] == codes.ok:
				fbSubData = storage.CreateFacebookSubscription( response[ 1 ][ "fb_uid" ], pebbleToken )
				fbUserData = storage.CreateUser( pebbleToken, response[ 1 ][ "fb_name" ] )
			else:
				logging.warning( "Problem requesting user data from facebook! status: " + str( response[ 0 ] ) + " response: " + str( response[ 1 ] ) )
		else:
			fbUserData = storage.FindUser( pebbleToken )
			
		return ( fbSubData, fbUserData )

	def Auth( self, params ):
		logging.debug( "Facebook Auth()" )
		
		import auth.devices
		response = auth.devices.GetAccess( self.request.headers[ 'X-User-Token' ], "facebook.config.auth", params[ "action" ] )
		
		data = response[ 1 ]
		
		if response[ 0 ] == codes.ok and response[ 1 ][ "status" ] == "success":
			fbData = self.GetOrCreateSubscription( self.request.headers[ 'X-User-Token' ] )
			
			fbSubData = fbData[ 0 ]
			fbUserData = fbData[ 1 ]
			
			if fbSubData is None:
				self.response.status = codes.internal_server_error
				self.response.data = { 'status' : "Create Subscription Failed" }
				return
				
			fbSubData.put()
			
			if fbUserData is not None:
				fbUserData.put()
				data[ "name" ] = fbUserData.name
		
		self.response.status = response[ 0 ]
		self.response.data = data

	def Events( self, params ):
		logging.debug( "Facebook Events()" )
		
		activateSub = params[ "action" ] == "subscribe"
		pebbleToken = self.request.headers[ 'X-User-Token' ]
		
		db = self.CreateConfigDB( defines.PLATFORM )
		fbData = self.GetOrCreateSubscription( pebbleToken, db )
		
		fbSubData = fbData[ 0 ]
		
		if params[ "action" ] != "issubscribed":
			if fbSubData is not None:
				# update sub data
				fbSubData.events = activateSub
				fbSubData.put()
				
				# Grab all the events for the user
				if activateSub:
					events.Fetch( pebbleToken, db, fbSubData.key().name() )
			
		if fbSubData is None:
			self.response.status = codes.unauthorized
			self.response.data = { 'status' : "require_auth" }
			return
			
		if fbSubData.events:
			subscribed = "yes"
		else:
			subscribed = "no"
		
		response = \
		{
			'status' : "success",
			'subscribed' : subscribed
		}
		
		self.response.status = codes.ok
		self.response.data = response
