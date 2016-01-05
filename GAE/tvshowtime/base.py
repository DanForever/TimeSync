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
from datetime import timedelta

#Google imports
from google.appengine.api import taskqueue

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
	def User( self, pebbleToken, platformAccess = None ):
		import config.user
		
		db = self.CreateConfigDB( defines.PLATFORM )
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
		
		db = self.CreateConfigDB( defines.PLATFORM )
		if db is None:
			return ( requests.codes.unauthorized, "" )
		
		response = net.MakeRequest( config.agenda.CONFIG, db )
		
		status = requests.codes.ok
		data = response[ 1 ]
		if "episodes" in data:
			for episode in data[ "episodes" ]:
				user = storage.FindUser( pebbleToken )
				response = self.CreatePin( pebbleToken, episode, user )
				
				if response[ 0 ] != requests.codes.ok:
					if response[ 1 ][ "message" ] == "INVALID_USER_TOKEN":
						logging.warning( "we've been given a duff user token, backing off" )
						
						status = requests.codes.bad_request
						data = { 'status' : "invalid_watch_token" }
						break 
		
		logging.debug( "Agenda() Finished" )
		
		return ( status, data )
		
	def UpdateSubscription( self, sub ):
		pebbleToken = sub.key().name()
		
		logging.debug( "UpdateSubscription(): " + str( pebbleToken ) )
		
		# Grab the URL for updating the user's agenda
		url = self.GetUrl \
		(
			"mainhandler",
			{
				'handler'	: "tvshowtime",
				'branch'	: "agenda",
				'action'	: "update"
			},
			full = False,
			scheme = None
		)
		
		# Use this to make the name of the task vaguely unique, assuming we don't
		# want to allow the task to execute more frequently than once a minute
		nameDate = datetime.utcnow().strftime( "Date%Y-%m-%dT%H-%M-" )
		
		config = \
		{
			'name' : "TVST-Sub-" + nameDate + str( pebbleToken ),
			'url' : url,
			'method' : "POST",
			'headers' :
			{
				'X-User-Token' : pebbleToken
			}
		}
		
		logging.debug( "Creating Task: " + str( config ) )
		
		try:
			taskqueue.add( **config )
		except ( taskqueue.TaskAlreadyExistsError, taskqueue.TombstonedTaskError ) as e:
			logging.warning( "Couldn't create task due to name conflict with previously created task: " + str( e ) )
			return ( requests.codes.too_many_requests, { 'status' : "Too soon" } )
		return ( requests.codes.ok, { 'status' : "success" } )
		
	def Checkin( self, pebbleToken, action ):
		import config.checkin
		import config.episode
		
		episodeId = self.request.headers[ defines.PEBBLE_PIN_ACT_EP_KEY ]
		
		db = self.CreateConfigDB( defines.PLATFORM )
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
		
		#Delete old pins which have the date embedded in the id
		oldId = "ts-tvst-agenda-" + str( user.id ) + "-" + str( episode[ "id" ] ) + "-" + str( episode[ "air_date" ] )
		pebble.Pin.Delete( oldId, pebbleToken )
		
		id = "ts-tvst-agenda-" + str( user.id ) + "-" + str( episode[ "id" ] )
		timeStr = episode[ "air_date" ] + " " + episode[ "air_time" ]
		subtitle = episode[ "network" ]
		source = "TVShow Time"
		
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
			#24 hour clock (when user has local time selected)
			time = datetime.strptime( timeStr, "%Y-%m-%d %H:%M" )
		except Exception as first:
			try:
				#12 hour clock (when user has network time selected)
				time = datetime.strptime( timeStr, "%Y-%m-%d %I:%M %p" )
			except Exception as second:
				try:
					#12 hour short clock (something inconsistant with the data returned from tvshowtime)
					time = datetime.strptime( timeStr, "%Y-%m-%d %I%p" )
				except Exception as third:
					logging.error( "Failed to convert as 24 hour clock: " + str( first ) )
					logging.error( "Failed to convert as 12 hour clock: " + str( second ) )
					logging.error( "Failed to convert as 12 hour short: " + str( third ) )
					logging.error( "Episode: " + str( episode ) )
					
					# Can't deal with this pin for some reason
					return ( requests.codes.ok, "INVALID_TIME_FORMAT" )
		
		if user.hourOffset is not None:
			hourOffset = timedelta( hours = user.hourOffset )
			time = time + hourOffset
		
		pin = pebble.Pin( pebbleToken, id, time, episode[ "show" ][ "name" ], defines.PEBBLE_ICON, subtitle = subtitle, headings = headings, paragraphs = paragraphs, source = source )
		
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