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

#system imports
import datetime
import logging

#library imports
import requests

#Project imports
import secrets.facebook
import defines

### Acquiring Authentication with Facebook ###
def GetNewDeviceLoginCode():
	logging.debug( "Facebook Net GetNewDeviceLoginCode()" )
	
	payload = \
	{
		'type' : 'device_code',
		'client_id' : secrets.facebook.CLIENT_ID,
		'scope' : 'user_events'
	}
	
	response = requests.post( defines.URL_BASE + defines.URL_SUB_AUTH, params = payload )
	
	logging.debug( "Facebook Net GetNewDeviceLoginCode() Response:\n" + response.text )
	return ( response.status_code, response.json() )
	
def GetDeviceLoginCodeStatus( code ):
	logging.debug( "Facebook Net GetDeviceLoginCodeStatus()" )
	payload = \
	{
		'type' : 'device_token',
		'client_id' : secrets.facebook.CLIENT_ID,
		'code' : code
	}
	
	response = requests.post( defines.URL_BASE + defines.URL_SUB_AUTH, params = payload )
	
	logging.debug( "Facebook Net GetNewDeviceLoginCode() Response:\n" + response.text )
	return ( response.status_code, response.json() )

### Retrieving user data ###
def GetCurrentUserData( accessToken ):
	url = defines.URL_BASE + defines.PLATFORM_VERSION + "/me"
	
	payload = \
	{
		'access_token' : accessToken,
	}
	
	response = requests.get( url, params = payload )
	return ( response.status_code, response.json() )
	
def GetEvents( accessToken ):
	url = defines.URL_BASE + defines.PLATFORM_VERSION + "/me/events"
	
	# Since the timeline can't be populated with anything older than 2 days ago
	# We limit the query to recent and future events
	since = datetime.datetime.now( defines.UTC ) - datetime.timedelta( days = 2 )
	
	nowInFacebookFormat = defines.DateTimeToISO8601( since )
	
	payload = \
	{
		'access_token' : accessToken,
		'since' : nowInFacebookFormat
	}
	
	response = requests.get( url, params = payload )
	return ( response.status_code, response.json() )