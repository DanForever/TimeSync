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
import importlib
import datetime
from json import dumps as jsonToString

#library imports
import requests

#Project imports
import storage

#config = \
#{
#	'url' : defines.URL_BASE + defines.URL_SUB_AUTH,
#	'out_map' :
#	{
#		
#	}
#	
#	'in_map' :
#	{
#		
#	}
#}
#
#{
#  "code": "92a2b2e351f2b0b3503b2de251132f47",
#  "user_code": "A1NWZ9",
#  "verification_uri": "https://www.facebook.com/device",
#  "expires_in": 420,
#  "interval": 5
#}
#
#{
#    "result": "OK",
#    "device_code": "_5B0ITpBvqY2kn5wT4ry",
#    "user_code": "3643-51a4",
#    "verification_url": "https://www.tvshowtime.com/activate",
#    "expires_in": 900,
#    "interval": 5
#}
#
## TV Showtime
#config = \
#{
#	'request' :
#	{
#		'url' : "https://api.tvshowtime.com/v1/oauth/device/code",
#		'method' : 'POST',
#		
#		# form encoded
#		'data' :
#		{
#			'client_id' : "Jv4oAhmEZfWehOZMXuJ5"
#		}
#	}
#	
#	'response' :
#	{
#		requests.codes.ok :
#		{
#			'public_key' : "user_code",
#			'private_key' : "device_code",
#			'url' : "verification_url",
#			'expires' : "expires_in",
#			'interval' : "interval"
#		}
#	}
#}

def SetDictEntry( source, config, value ):
	path = config[ 0 ]
	return reduce( dict.__getitem__, path, source ).update( { config[ 1 ] : value } )

def FindDictEntry( source, path ):
	return reduce( dict.__getitem__, path, source )
	
def MapResponse( map, response ):
	out = {}
	for key, value in map.iteritems():
		out[ key ] = response[ value ]
	return out

def MakeRequest( config ):
	response = requests.request( **config[ "request" ] )
	responseObject = response.json()
	
	successConfig = config[ "response" ][ "success" ]
	if response.status_code == successConfig[ "status" ] and successConfig[ "exists" ] in responseObject:
		out = MapResponse( successConfig[ "map" ], responseObject )
		status = requests.codes.ok
	else:
		out = MapResponse( config[ "response" ][ "failure" ][ "map" ], responseObject )
		status = requests.codes.bad_request
	return ( status, out )

def StoreAccess( pebbleToken, params, platform ):
	params[ "watch" ] = storage.CreateWatch( pebbleToken )
	params[ "platform" ] = platform
	access = storage.CreateAccess( **params )
	access.put()

def HasAccess( pebbleToken, platform ):
	accessToken = storage.FindPlatformAccessCode( pebbleToken, platform )
	
	if accessToken is not None:
		return True
	return False

def GetExistingRequest( pebbleToken, platform ):
	# Find an auth request for the specified pebble
	authRequest = storage.FindPlatformAuthRequest( pebbleToken, platform )
	
	if authRequest is not None:
		#check to see if the request is still valid
		expired = datetime.datetime.utcnow() > authRequest.expires
		
		if expired:
			# Delete the old request
			logging.debug( "Auth Request expired (Deleting)" )
			authRequest.delete()
			authRequest = None
		else:
			logging.debug( "Auth Request found" )
	else:
		logging.debug( "Auth Request not found" )
		
	return authRequest

def StoreRequest( pebbleToken, params, platform ):
	# Convert the specified time limit into a datetime object
	params[ "expires" ] = datetime.datetime.utcnow() + datetime.timedelta( seconds = params[ 'expires' ] )

	# Create parent object, this does not need to be written to the
	# database as it's only purpose is to contain the pebble token
	params[ "watch" ] = storage.CreateWatch( pebbleToken )
	
	params[ "platform" ] = platform
	
	authRequest = storage.CreatePlatformAuthRequest( **params )
	authRequest.put()
	
	return authRequest

def GenerateResponse( authRequest ):
	if authRequest:
		status = requests.codes.ok
		response = \
		{
			"status" : "require_auth",
			"url" : authRequest.user_uri,
			"code" : authRequest.user_code,
			"interval" : authRequest.update_interval
		}
	else:
		status = requests.codes.bad_request
		response = \
		{
			"status" : "no_auth",
			"error" : "No authorisation code found"
		}
		
	return ( status, jsonToString( response ) )

def StandardSuccessReturn():
	response = { 'status' : "success" }
	return ( requests.codes.ok, jsonToString( response ) )

def CheckRequest( pebbleToken, configLib, createIfRequired ):
	# See if we've already got an authorisation request pending
	authRequest = GetExistingRequest( pebbleToken, configLib.PLATFORM )
	
	if authRequest:
		config = configLib.AUTH_KEY_POLL
		
		# Fill in the private key in the poll configuration
		SetDictEntry( config, config[ "private_key_entry" ], authRequest.auth_code )
		
		# Poll the server to check on the status of the authorisation process
		response = MakeRequest( config )
		
		if response[ 0 ] == requests.codes.ok:
			# The user has entered the pin into the service platform, store the resultant access token
			StoreAccess( pebbleToken, response[ 1 ], configLib.PLATFORM )
			
			return StandardSuccessReturn()

	elif createIfRequired:
		# Send a new authorisation request to the specified service platform
		response = MakeRequest( configLib.AUTH_KEY_REQUEST )
		
		# Store the authorisation request details
		authRequest = StoreRequest( pebbleToken, response[ 1 ], configLib.PLATFORM )
	
	return GenerateResponse( authRequest )

def GetAccess( pebbleToken, configPath, createIfRequired ):
	configLib = importlib.import_module( configPath )
	
	# Check to see if we've already been through the whole login authentication rigamarole
	if HasAccess( pebbleToken, configLib.PLATFORM ):
		logging.debug( "GetAccess() User has access" )
		return StandardSuccessReturn()
	
	return CheckRequest( pebbleToken, configLib, createIfRequired )