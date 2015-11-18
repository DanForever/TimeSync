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
	def ProcessWrapper( self, params ):
		self.Process( params[ "branch" ], params[ "action" ] )
		
	def Process( self, branch, action ):
		branches = \
		{
			"auth" : self.Auth,
			"agenda" : self.AgendaSubscription,
			"checkin" : self.Checkin
		}
		
		actions = \
		{
			# Auth Actions
			"request" : True,
			"query"	: False,
			
			"subscribe" : "add",
			"unsubscribe" : "remove",
			"issubscribed" : "check",
			"update" : "update",
			
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
		
		outdata = response[ 1 ]
		
		#Fetch and store username
		if response[ 0 ] == requests.codes.ok:
			user = self.User( pebbleToken, response[ 2 ] )
			if user:
				outdata[ "name" ] = user.name
		
		self.response.status = response[ 0 ]
		self.response.data = outdata
	
	def AgendaSubscription( self, pebbleToken, action ):
		if self.CreateConfigDB( pebbleToken ) is None:
			self.response.status = requests.codes.unauthorized
			self.response.data = { 'status' : "require_auth" }
			return
		
		self.response.status = requests.codes.ok
		self.response.data = { 'status' : "success" }
			
		if action == "add":
			# Add the subscription so that it'll be picked up by later 
			sub = storage.StoreSubscription( pebbleToken )
			
			# Immediately populate with pins (Using a push task to do so)
			self.UpdateSubscription( sub )
			
		elif action == "remove":
			storage.DeleteSubscription( pebbleToken )
		elif action == "update":
			# Update directly, be warned, could time out if it's not run from a task!
			response = self.Agenda( pebbleToken )
			
			# We can't return anything other than 200 OK here because a failure will
			# prompt a push task to retry, but the conditions for failure won't have changed
			if self.response.status != requests.codes.ok:
				logging.warning( "AgendaSubscription() Update: " + str( response ) )
				self.response.data = response[ 1 ]
		else:
			sub = storage.FindSubscription( pebbleToken )
			if sub is None:
				self.response.data[ "subscribed" ] = "no"
			else:
				self.response.data[ "subscribed" ] = "yes"
			
