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

# Library Imports
import requests

#Project imports
import base
import storage

class Handler( base.Handler ):
	def Process( self, branch, action ):
		branches = \
		{
			"auth" : self.Auth,
			"agenda" : self.Agenda,
			"subscribe" : self.Subscribe,
			"checkin" : self.Checkin
		}
		
		actions = \
		{
			# Auth Actions
			"request" : True,
			"query"	: False,
			
			"subscribe" : True,
			"unsubscribe" : False,
			
			"populate" : True,
			
			"watch" : "WATCH",
			"unwatch" : "UNWATCH"
		}
		
		if branch not in branches or action not in actions:
			self.response.status = requests.codes.not_found
			return
		
		pebbleToken = self.request.headers[ 'X-User-Token' ]
		
		branches[ branch ]( pebbleToken, actions[ action ] )
		
	def Auth( self, pebbleToken, action ):
		import auth.devices
		
		response = auth.devices.GetAccess( pebbleToken, "tvshowtime.config.auth", action )
		
		#Fetch and store username
		if response[ 0 ] == requests.codes.ok:
			self.User( pebbleToken, response[ 2 ] )
		
		self.response.status = response[ 0 ]
		self.response.data = response[ 1 ]
	
	def Subscribe( self, pebbleToken, action ):
		if self.CreateConfigDB( pebbleToken ) is None:
			self.response.status = requests.codes.unauthorized
			return
		
		if action:
			storage.StoreSubscription( pebbleToken )
		else: 
			storage.DeleteSubscription( pebbleToken )
		self.response.status = requests.codes.ok
