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
from json import dumps as jsonToString

#Library imports
from requests import codes

#Project imports
import common.base
import storage
import logging
import events

class Handler( common.base.Handler ):
	def Auth( self, params ):
		logging.debug( "Facebook Auth()" )
		
		import auth.devices
		response = auth.devices.GetAccess( self.request.headers[ 'X-User-Token' ], "facebook.config.auth", params[ "action" ] )
		
		self.response.status = response[ 0 ]
		self.response.data = response[ 1 ]
		
	def Events( self, params ):
		logging.debug( "Facebook Events()" )
		
		activateSub = params[ "action" ] == "subscribe"
		pebbleToken = self.request.headers[ 'X-User-Token' ]
		
		# update sub data
		fbSubData = storage.FindFacebookSubscriptionByWatchToken( pebbleToken )
		
		if params[ "action" ] != "issubscribed":
			fbSubData.events = activateSub
			fbSubData.put()
		
		if activateSub:
			# Grab all the events for the user
			events.Fetch( pebbleToken, fbSubData.key().name() )
		
		if fbSubData is not None and fbSubData.events:
			subscribed = "yes"
		else:
			subscribed = "no"
		
		response = \
		{
			'status' : "success",
			'subscribed' : subscribed
		}
		self.response.status = codes.ok
		self.response.data = jsonToString( response )
		