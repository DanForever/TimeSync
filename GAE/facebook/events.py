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
import logging

#library imports
from requests import codes

#Project imports
import storage
import net
import defines
import pebble
import auth.keys

RSVP = \
{
	'attending'		: "Attending",
	'unsure' 		: "Interested",
	'declined'		: "Declined",
	'not_replied' 	: "Not replied"
}

def Fetch( pebbleToken, db, fbuid ):
	import config.user
	
	# Since the timeline can't be populated with anything older than 2 days ago
	# We limit the query to recent and future events
	since = datetime.datetime.now( defines.UTC ) - datetime.timedelta( days = 2 )
	db[ defines.START_DATE_KEY ] = defines.DateTimeToISO8601( since )
	
	response = net.MakeRequest( config.user.EVENTS, db )
	
	if response[ 0 ] == codes.ok:
		logging.debug( "Events returned: " + str( response[ 1 ][ "events" ] ) )
		AddEvents( pebbleToken, response[ 1 ][ "events" ], fbuid )

def AddEvents( pebbleToken, events, fbuid ):
	for event in events:
		response = AddEvent( pebbleToken, event, fbuid )
		
		if response[ 0 ] != codes.ok:
			if response[ 1 ][ "message" ] == "INVALID_USER_TOKEN":
				logging.warning( "we've been given a duff user token, backing off" )
				
				status = codes.bad_request
				data = { 'status' : "invalid_watch_token" }
				break 

def AddEvent( pebbleToken, event, fbuid ):
	logging.debug( "Event '" + event[ 'name' ] + "', ID: " + event[ 'id' ] )
	data = \
	{
		'pebbleToken' : pebbleToken,
		'id' : "ts-fbev-" + str( fbuid ) + "-" + str( event[ 'id' ] ),
		'time' : defines.ISO8601ToDateTime( event[ 'start_time' ] ).astimezone( defines.UTC ),
		'title' : event[ 'name' ],
		'icon' : "system://images/NOTIFICATION_FACEBOOK",
		'source' : "Facebook Events",
		'headings' :
		[
			"Description",
			"RSVP Status"
		],
		'paragraphs' :
		[
			event[ 'description' ],
			RSVP[ event[ 'rsvp_status' ] ]
		]
	}
	
	if "end_time" in event:
		endTime = defines.ISO8601ToDateTime( event[ 'end_time' ] )
		delta = endTime - data[ "time" ]
		data[ "duration" ] = (int)( delta.total_seconds() / 60 )
	
	pin = pebble.Pin( **data )
	
	return pin.Send()

