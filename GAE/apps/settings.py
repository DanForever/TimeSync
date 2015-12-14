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

#System Imports
import os
import logging

#Google Imports
import webapp2
from google.appengine.ext.webapp import template

#Library Imports
from requests import codes

#Project Imports
import auth
import tvshowtime.storage
import facebook.storage

class SettingsViewHandler( webapp2.RequestHandler ):
	def get( self, pebbleToken ):
		facebookEventsSub = facebook.storage.FindFacebookSubscriptionByWatchToken( pebbleToken )
		tvshowtimeUser = tvshowtime.storage.FindUser( pebbleToken )
		
		if tvshowtimeUser is not None and tvshowtimeUser.hourOffset is not None:
			tvstHourOffset = tvshowtimeUser.hourOffset
		else:
			tvstHourOffset = 0
		
		params = \
		{
			"pebbleToken" : pebbleToken,
			
			"tvst" :
			{
				"hasAuth" : ( "false", "true" )[ auth.HasAccess( pebbleToken, "tvshowtime.config.auth" ) == True ],
				"agenda" : ( "false", "true" )[ tvshowtime.storage.FindSubscription( pebbleToken ) is not None ],
				"hourOffset" : tvstHourOffset
			},
			
			"facebook" :
			{
				"hasAuth" : ( "false", "true" )[ auth.HasAccess( pebbleToken, "facebook.config.auth" ) == True ],
				"events" : ( "false", "true" )[ facebookEventsSub is not None and facebookEventsSub.events ]
			}
		}
		
		logging.debug( "SettingsViewHandler get() params: " + str( params ) )
		
		output = template.render( "templates/pebble_config/settings.html", params )
		
		self.response.set_status( codes.ok )
		self.response.write( output )

def fb( data, pebbleToken ):
	if auth.HasAccess( pebbleToken, "facebook.config.auth" ):
		facebookEventsSub = facebook.storage.FindFacebookSubscriptionByWatchToken( pebbleToken )
		
		if facebookEventsSub is not None:
			facebookEventsSub.events = data[ "subscribed" ]
			facebookEventsSub.put()
		else:
			logging.error( "Facebook user is missing subscription storage object!" )

def tvst( data, pebbleToken ):
	if auth.HasAccess( pebbleToken, "tvshowtime.config.auth" ):
		subscription = tvshowtime.storage.FindSubscription( pebbleToken )
		if data[ "subscribed" ]:
			if subscription is None:
				tvshowtime.storage.StoreSubscription( pebbleToken )
		else:
			if subscription is not None:
				subscription.delete()
		
		user = tvshowtime.storage.FindUser( pebbleToken )
		
		if user is not None:
			user.hourOffset = int( data[ "hourOffset" ] )
			user.put()
		else:
			logging.error( "TVST user is missing user storage object!" )
		
class SettingsSaveHandler( webapp2.RequestHandler ):
	def post( self, pebbleToken ):
		
		if pebbleToken is None or pebbleToken == "undefined":
			self.response.set_status( codes.unauthorized )
			return
		
		logging.debug( "Saving settings for user: " + pebbleToken )
		logging.debug( "Settings JSON: " + str( self.request.body ) )
		
		from json import loads as stringToJson
		data = stringToJson( self.request.body )
		
		fb( data[ "fbev" ], pebbleToken )
		tvst( data[ "tvst" ], pebbleToken )
		
		self.response.set_status( codes.ok )

app = webapp2.WSGIApplication \
(
	[
		( r'/v\d*/settings/view/([\d\w]*)/', SettingsViewHandler ),
		( r'/v\d*/settings/save/([\d\w]*)/?', SettingsSaveHandler ),
	],
	debug = os.environ[ 'SERVER_SOFTWARE' ].startswith( 'Development' )
)
