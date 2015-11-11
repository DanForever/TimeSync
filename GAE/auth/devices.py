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

#library imports
import requests

#Project imports
import storage
import net

def StoreAccess( pebbleToken, params, platform ):
	params[ "watch" ] = storage.CreateWatch( pebbleToken )
	params[ "platform" ] = platform
	access = storage.CreateAccess( **params )
	access.put()
	return access

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
		status = requests.codes.unauthorized
		response = \
		{
			"status" : "no_auth",
			"error" : "No authorisation code found"
		}
		
	return ( status, response, authRequest )

def StandardSuccessReturn( platformAccess ):
	response = { 'status' : "success" }
	return ( requests.codes.ok, response, platformAccess )

def CheckRequest( pebbleToken, configLib, createIfRequired ):
	# See if we've already got an authorisation request pending
	authRequest = GetExistingRequest( pebbleToken, configLib.PLATFORM )
	
	if authRequest:
		config = configLib.AUTH_KEY_POLL
		
		# Fill in the private key in the poll configuration
		db = \
		{
			"private_key" : authRequest.auth_code
		}
		
		# Poll the server to check on the status of the authorisation process
		response = net.MakeRequest( config, db )
		
		logging.debug( "CheckRequest() response: " + str( response ) )
		
		if response[ 0 ] == requests.codes.ok:
			# The user has entered the pin into the service platform, store the resultant access token
			platformAccess = StoreAccess( pebbleToken, response[ 1 ], configLib.PLATFORM )
			
			return StandardSuccessReturn( platformAccess )

	elif createIfRequired:
		# Send a new authorisation request to the specified service platform
		response = net.MakeRequest( configLib.AUTH_KEY_REQUEST )
		
		# Store the authorisation request details
		authRequest = StoreRequest( pebbleToken, response[ 1 ], configLib.PLATFORM )
	
	return GenerateResponse( authRequest )

def GetAccess( pebbleToken, configPath, createIfRequired ):
	configLib = importlib.import_module( configPath )
	
	# Check to see if we've already been through the whole login authentication rigamarole
	platformAccess = storage.FindPlatformAccessCode( pebbleToken, configLib.PLATFORM )
	if platformAccess is not None:
		logging.debug( "GetAccess() User has access" )
		return StandardSuccessReturn( platformAccess )
	
	return CheckRequest( pebbleToken, configLib, createIfRequired )
