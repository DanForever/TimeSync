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
from datetime import datetime

# Library Imports
import requests

#Project imports
import common.base
import defines
import pebble
import net
import auth.keys
import common.storage
import storage

class Handler( common.base.Handler ):
	def CreateConfigDB( self, pebbleToken, platformAccess = None ):
		
		if platformAccess is None:
			platformAccess = common.storage.FindPlatformAccessCode( pebbleToken, defines.PLATFORM )
			if platformAccess is None:
				return None
		
		db = \
		{
			auth.keys.ACCESS_TOKEN_KEY : platformAccess.token
		}
		
		return db
	
	def User( self, pebbleToken, platformAccess = None ):
		import config.user
		
		db = self.CreateConfigDB( pebbleToken )
		if db is None:
			return None
		
		response = net.MakeRequest( config.user.CONFIG, db )
		
		if response[ 0 ] != requests.codes.ok:
			return None
			
		user = response[ 1 ][ config.user.USER_KEY ]
		id = user[ "id" ]
		name = user[ "name" ]
		return storage.StoreUser( pebbleToken, id, name )
	
	def Agenda( self, pebbleToken ):
		import config.agenda
		
		db = self.CreateConfigDB( pebbleToken )
		if db is None:
			return ( requests.codes.unauthorized, "" )
		
		response = net.MakeRequest( config.agenda.CONFIG, db )
		
		for episode in response[ 1 ][ "episodes" ]:
			user = storage.FindUser( pebbleToken )
			response = self.CreatePin( pebbleToken, episode, user )
			
			if response[ 0 ] != requests.codes.ok:
				logging.warning( "Failed to create TVST pin: " + str( response ) )
		
		return ( response[ 0 ], "" )
		
	def Checkin( self, pebbleToken, action ):
		import config.checkin
		import config.episode
		
		episodeId = self.request.headers[ defines.PEBBLE_PIN_ACT_EP_KEY ]
		
		db = self.CreateConfigDB( pebbleToken )
		if db is None:
			self.response.status = requests.codes.unauthorized
			return
		db[ defines.PEBBLE_PIN_ACT_EP_KEY ] = str( episodeId )
		
		# Tell TV Showtime to mark the episode correctly
		checkinConfig = getattr( config.checkin, action )
		checkinResponse = net.MakeRequest( checkinConfig, db )
		
		if checkinResponse[ 0 ] == requests.codes.ok:
			#Check in/out successful - update pin
			fetchEpisodeResponse = net.MakeRequest( config.episode.CONFIG, db )
			if fetchEpisodeResponse[ 0 ] == requests.codes.ok:
				self.CreatePin( pebbleToken, fetchEpisodeResponse[ 1 ][ "episode" ] )
			else:
				self.response.status = fetchEpisodeResponse[ 0 ]
				logging.error( "Error fetching episode: " + str( fetchEpisodeResponse[ 1 ] ) )
		else:
			self.response.status = checkinResponse[ 0 ]
			logging.error( "Error checking in: " + str( checkinResponse[ 1 ] ) )
	
	def CreatePin( self, pebbleToken, episode, user = None ):
		
		if user is None:
			user = storage.FindUser( pebbleToken )
			if user is None:
				return ( requests.codes.unauthorized, "" )
		
		id = "ts-tvst-agenda-" + str( user.id ) + "-" + str( episode[ "id" ] ) + "-" + str( episode[ "air_date" ] )
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
				
				# Can't deal with this pin for some reason
				return
		
		pin = pebble.Pin( pebbleToken, id, time, episode[ "show" ][ "name" ], defines.PEBBLE_ICON, subtitle = subtitle, headings = headings, paragraphs = paragraphs )
		
		if episode[ "seen" ]:
			action = \
			{
				'title'		: "Check out",
				'urlaction'	: "unwatch"
			}
		else:
			action = \
			{
				'title'		: "Check in",
				'urlaction'	: "watch"
			}
		
		# Add checkin action
		url = self.GetUrl \
		(
			"mainhandler",
			{
				'handler'	: "tvshowtime",
				'branch'	: "checkin",
				'action'	: action[ "urlaction" ]
			}
		)
		
		headers = \
		{
			'X-User-Token'					: pebbleToken,
			defines.PEBBLE_PIN_ACT_EP_KEY	: str( episode[ "id" ] )
		}
		
		pin.AddAction( action[ "title" ], url, headers )
		
		return pin.Send()