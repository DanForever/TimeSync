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

#Library imports
import requests

#Project imports
import common.base
import storage
import logging
import defines as defines
import net as net
import events as events

class Handler( common.base.Handler ):
	def Auth( self, params ):
		logging.debug( "Facebook Auth()" )
		pebbleToken = self.request.headers[ 'X-User-Token' ]
		
		import auth.devices
		response = auth.devices.GetAccess( pebbleToken, "facebook.config.auth", params[ "action" ] )
		
		self.response.status = response[ 0 ]
		self.response.data = response[ 1 ]
		
	def ProcessWrapper( self, params ):
		self.Process( params[ "branch" ], params[ "action" ] )
		
	def Process( self, branch, action ):
		branches = \
		{
			"events" : self.SubscribeEvents
		}
		
		actions = \
		{
			"subscribe" : "yes",
			"unsubscribe" : "no",
			"issubscribed" : "check",
			
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
		
		activateSub = action == "yes"
		
		# update sub data
		fbSubData = storage.FindFacebookSubscriptionByWatchToken( pebbleToken )
		
		if action != "check":
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
		self.response.status = requests.codes.ok
		self.response.data = jsonToString( response )
		