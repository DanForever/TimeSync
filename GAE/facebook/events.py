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
import logging

#library imports
import requests

#Project imports
import storage
import net
import defines

def Fetch( pebbleToken, fbuid ):
	# Check to see if we already have facebook access
	access = storage.FindPlatformAccessCode( pebbleToken, defines.PLATFORM )
	
	if not access:
		return False
	
	status = net.GetEvents( access.token )
	
	if status[ 0 ] == requests.codes.ok:
		Process( pebbleToken, status[ 1 ][ 'data' ], fbuid )
		return True
		
	else:
		return False

def Process( pebbleToken, events, fbuid ):
	# Create parent object, this does not need to be written to the
	# database as it's only purpose is to contain the pebble token
	watch = storage.CreateWatch( pebbleToken )
	
	for event in events:
		logging.debug( "Event '" + event[ 'name' ] + "', ID: " + event[ 'id' ] )
		
		# We need to associate the key with facebook events
		# ts-fbev-XXXXXXXXXXXXXXXX-YYYYYYYYYYYYYYYYY
		key = "ts-fbev-" + str( fbuid ) + "-" + str( event[ 'id' ] )
		
		startTime = defines.ISO8601ToDateTime( event[ 'start_time' ] )
		
		if 'description' in event:
			description = event[ 'description' ]
			
			if len( description ) > 1023:
				description = description[ : 1000 ] + "..."
		else:
			description = "No description"
		
		pin = storage.CreateWatchPin( watch, key, event[ 'name' ], description, startTime )
		pin.put()
		
		#Convert time to UTC
		startTimeUtc = startTime.astimezone( defines.UTC )
		
		#Construct HTTP put request
		pebbleDateFormat = "%Y-%m-%dT%H:%M:%SZ"
		eventTimeInPebbleFormat = startTimeUtc.strftime( pebbleDateFormat )
		
		body = \
		{
			'id' 		: key,
			'time' 		: eventTimeInPebbleFormat,
			'layout'	: \
			{
				'type' 		: "genericPin",
				'title' 	: event[ 'name' ],
				'tinyIcon'	: "system://images/NOTIFICATION_FACEBOOK",
				'body' 		: description
			}
		}
		
		headers = \
		{
			'X-User-Token' : pebbleToken,
			'Content-Type' : "application/json"
		}
		
		url = "https://timeline-api.getpebble.com/v1/user/pins/" + key;
		bodyStr = jsonToString( body )
		
		response = requests.put( url = url, headers = headers, data = bodyStr )
		
		logging.debug( "Pin URL: " + str( response.url ) )
		logging.debug( "Pin Data: " + bodyStr )
		logging.debug( "Pin Headers: " + str( headers ) )
		
		logging.debug( "Pin response status: " + str( response.status_code ) )
		logging.debug( "Pin response data: " + response.text )
