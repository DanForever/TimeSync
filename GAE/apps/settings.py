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
	def get( self ):
		#var hasTVShowTimeAuth = false;
		#var tvstIsSubscribedToAgenda = false;
		#var tvstHourOffsetInitialValue = 0;
		
		#var hasFacebookAuth = true;
		#var fbIsSubscribedToEvents = false;
		
		#Placeholder token
		pebbleToken = "abc123"
		
		facebookEventsSub = facebook.storage.FindFacebookSubscriptionByWatchToken( pebbleToken )
		
		params = \
		{
			"tvst" :
			{
				"hasAuth" : ( "false", "true" )[ auth.HasAccess( pebbleToken, "tvshowtime.config.auth" ) == True ],
				"agenda" : ( "false", "true" )[ tvshowtime.storage.FindSubscription( pebbleToken ) is not None ]
			},
			
			"facebook" :
			{
				"hasAuth" : ( "false", "true" )[ auth.HasAccess( pebbleToken, "facebook.config.auth" ) == True ],
				"events" : ( "false", "true" )[ facebookEventsSub is not None and facebookEventsSub.events ]
			}
		}
		
		output = template.render( "templates/pebble_config/settings.html", params )
		
		self.response.set_status( codes.ok )
		self.response.write( output )

class SettingsSaveHandler( webapp2.RequestHandler ):
	def post( self ):
		pass

app = webapp2.WSGIApplication \
(
	[
		( r'/v\d*/settings/view/?', SettingsViewHandler ),
		( r'/v\d*/settings/save/?', SettingsSaveHandler ),
	],
	debug = os.environ[ 'SERVER_SOFTWARE' ].startswith( 'Development' )
)
