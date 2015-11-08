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
import defines

class Handler( base.Handler ):
	def Process( self, branch, action ):
		branches = \
		{
			"auth" : self.Auth,
			"agenda" : self.Agenda,
		}
		
		actions = \
		{
			# Auth Actions
			"request" : True,
			"query"	: False,
			
			"populate": True,
		}
		
		if branch not in branches or action not in actions:
			self.response.status = requests.codes.not_found
			return
		
		pebbleToken = self.request.headers[ 'X-User-Token' ]
		
		branches[ branch ]( pebbleToken, actions[ action ] )
		
	def Auth( self, pebbleToken, action ):
		
		import auth.devices
		
		response = auth.devices.GetAccess( pebbleToken, "tvshowtime.config.auth", action )
		self.response.status = response[ 0 ]
		self.response.data = response[ 1 ]
	
	def Agenda( self, pebbleToken, action ):
		import storage
		import net
		import config.agenda
		import pebble
		from datetime import datetime
		
		platformAccess = storage.FindPlatformAccessCode( pebbleToken, defines.PLATFORM )
		
		if platformAccess is None:
			self.response.status = requests.codes.unauthorized
			return
		
		db = \
		{
			'access_token' : platformAccess.token
		}
		
		logging.debug( "DB: " + str( db ) )
		response = net.MakeRequest( config.agenda.CONFIG, db )
		
		for episode in response[ 1 ][ "episodes" ]:
			id = "ts-tvst-agenda-" + str( episode[ "id" ] )
			timeStr = episode[ "air_date" ] + " " + episode[ "air_time" ]
			subtitle = episode[ "network" ]
			
			headings = \
			[
				"Title",
				"Number"
			]
			
			paragraphs = \
			[
				episode[ "name" ],
				"S{0:02n}E{1:02n}".format( episode[ "season_number" ], episode[ "number" ] )
			]
			
			try:
				time = datetime.strptime( timeStr, "%Y-%m-%d %H:%M" )
			except Exception as first:
				try:
					time = datetime.strptime( timeStr, "%Y-%m-%d %I:%M %p" )
				except Exception as second:
					logging.error( "Failed to convert as 24 hour clock: " + str( first ) )
					logging.error( "Failed to convert as 12 hour clock: " + str( second ) )
					
					#Can't deal with this pin for some reason, move onto the next one
					continue
			
			pin = pebble.Pin( pebbleToken, id, time, episode[ "show" ][ "name" ], defines.PEBBLE_ICON, subtitle = subtitle, headings = headings, paragraphs = paragraphs )
			
			pin.Send()
		
		self.response.status = response[ 0 ]
		