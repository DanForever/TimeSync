import requests
import webapp2
import storage
import datetime
from json import dumps as jsonToString
import logging
import iso8601
import secrets.facebook

PLATFORM = 'FACEBOOK'

ZERO = datetime.timedelta( 0 )

# naming scheme:
# Net = function involves a requests library call
# DB = function will read/write storage

# This class is a hack to avoid installing/importing pytz
class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset( self, dt ):
        return ZERO

    def tzname( self, dt ):
        return "UTC"

    def dst( self, dt ):
        return ZERO

class HTTPResponse():
	def __init__( self ):
		self.status = requests.codes.ok
		self.data = ""

class Handler():
	def __init__( self ):
		self.response = HTTPResponse()
	
	def Process( self, request, branch, action ):
		branches = \
		{
			"auth" : self.GetAccess,
			"events" : self.GetEvents
			#"birthdays" : Birthdays
		}
		
		actions = \
		{
			"subscribe" : True,
			"unsubscribe" : False,
			
			# Auth Actions
			"request" : True,
			"query"	: False
		}
		
		logging.debug( str( secrets.facebook.CLIENT_ID ) )
		
		if branch not in branches or action not in actions:
			self.response.status = requests.codes.not_found
			return
		
		pebbleToken = request.headers[ 'X-User-Token' ]
		
		branches[ branch ]( pebbleToken, actions[ action ] )

	def NetGetNewDeviceLoginCode( self ):
		baseUrl = 'https://graph.facebook.com/'
		subUrl = 'oauth/device'
		
		payload = \
		{
			'type' : 'device_code',
			'client_id' : secrets.facebook.CLIENT_ID,
			'scope' : 'user_events'
		}
		
		response = requests.post( baseUrl + subUrl, params = payload )
		
		logging.debug( "NetGetNewDeviceLoginCode() Response:\n" + response.text )
		return ( response.status_code, response.json() )
		
	def NetGetDeviceLoginCodeStatus( self, code ):
		baseUrl = 'https://graph.facebook.com/'
		subUrl = 'oauth/device'
		
		payload = \
		{
			'type' : 'device_token',
			'client_id' : secrets.facebook.CLIENT_ID,
			'code' : code
		}
		
		response = requests.post( baseUrl + subUrl, params = payload )
		
		logging.debug( "NetGetDeviceLoginCodeStatus() Response:\n" + response.text )
		
		return ( response.status_code, response.json() )

	def DBGetExistingDeviceAuthCode( self, pebbleToken ):
		# Find an auth request for the specified pebble
		authRequest = storage.FindPlatformAuthRequest( pebbleToken, PLATFORM )
		
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

	def DBCreateNewDeviceAuthCode( self, pebbleToken, authRequestResponse ):
		# Convert the specified time limit into a datetime object
		expirationTime = datetime.datetime.utcnow() + datetime.timedelta( seconds = authRequestResponse[ 'expires_in' ] )
		
		# Create parent object, this does not need to be written to the
		# database as it's only purpose is to contain the pebble token
		watch = storage.CreateWatch( pebbleToken )
		
		# Create the object
		authRequest = storage.CreatePlatformAuthRequest \
		(
			watch,
			PLATFORM,
			authRequestResponse[ 'code' ],
			authRequestResponse[ 'user_code' ],
			authRequestResponse[ 'verification_uri' ],
			expirationTime,
			authRequestResponse[ 'interval' ],
		)
		
		# Add it to the database
		authRequest.put()
		
		logging.debug( "Created auth request" )
		
		return authRequest

	def CheckLoginCodeStatus( self, pebbleToken, authRequest ):
		#todo: Check time since last poll?
		logging.debug( "Checking log in status with facebook" )
		status = self.NetGetDeviceLoginCodeStatus( authRequest.auth_code )
		
		if status[ 0 ] == requests.codes.ok:
			# Create parent object, this does not need to be written to the
			# database as it's only purpose is to contain the pebble token
			watch = storage.CreateWatch( pebbleToken )
			
			accessToken = status[ 1 ][ 'access_token' ]
			access = storage.CreateAccess( watch, PLATFORM, accessToken )
			
			# store it in the database
			access.put()
			
			self.response.status = requests.codes.ok
			
			response = \
			{
				'status' : "success",
			}
			
		else:
			self.response.status = requests.codes.bad_request
			
			response = \
			{
				'status' : "error",
				'message' : status[ 1 ][ 'error' ][ 'message' ],
				'user_code' : authRequest.user_code
			}
		
		self.response.data = jsonToString( response )

	def CheckPlatformAccess( self, pebbleToken ):
		# Check to see if we already have facebook access
		access = storage.FindPlatformAccessCode( pebbleToken, PLATFORM )
		
		if access:
			response = \
			{
				'status' : "success",
			}
			self.response.status = requests.codes.ok
			self.response.data = jsonToString( response )
			return True
		return False
	
	def GetAccess( self, pebbleToken, createIfRequired ):
		
		if self.CheckPlatformAccess( pebbleToken ):
			return
		
		# Check to see if we already have facebook access
		accessToken = storage.FindPlatformAccessCode( pebbleToken, PLATFORM )
		
		if accessToken:
			response = \
			{
				'status' : "success",
			}
			self.response.status = requests.codes.ok
			self.response.data = jsonToString( response )
			return
		
		# No access code yet, perhaps we've already got an existing auth request on the go?
		authRequest = self.DBGetExistingDeviceAuthCode( pebbleToken )
		
		if authRequest is None and createIfRequired:
			# No existing auth request found for this watch
			logging.debug( "Creating new auth request" )
			
			# Request new code from facebook
			authRequestResponse = self.NetGetNewDeviceLoginCode()[ 1 ]
			
			# Store new request
			authRequest = self.DBCreateNewDeviceAuthCode( pebbleToken, authRequestResponse )
		elif authRequest:
			# Check status
			self.CheckLoginCodeStatus( pebbleToken, authRequest )
			return
		
		if authRequest:
			logging.debug( "Turning auth request into json response" )
			
			returnData = \
			{
				"status" : "require_auth",
				"url" : authRequest.user_uri,
				"code" : authRequest.user_code,
				"interval" : authRequest.update_interval
			}
			
			self.response.status = requests.codes.ok
			self.response.data = jsonToString( returnData )
			
		else:
			logging.debug( "No auth request - creating json error response" )
			
			returnData = \
			{
				"status" : "no_auth",
				"error" : "No authorisation code found"
			}
			
			self.response.status = requests.codes.bad_request
			self.response.data = jsonToString( returnData )

	def DateTimeToISO8601( self, dt ):
		outputFormat = "%Y-%m-%dT%H:%M:%S%z"
		return dt.strftime( outputFormat )
	
	def ISO8601ToDateTime( self, strDt ):
		return iso8601.parse_date( strDt )
		
	def DateTimeToPbl( self, dt ):
		format = self.DateTimeToISO8601( dt )
		return format[:-2] + ":" + format[-2:]
		
	def NetGetEvents( self, accessToken ):
		url = "https://graph.facebook.com/v2.4/me/events"
		
		# Since the timeline can't be populated with anything older than 2 days ago
		# We limit the query to recent and future events
		since = datetime.datetime.now( UTC() ) - datetime.timedelta( days = 2 )
		
		nowInFacebookFormat = self.DateTimeToISO8601( since )
		#facebookDateFormat = "%Y-%m-%dT%H:%M:%S+0000"
		#nowInFacebookFormat = since.strftime( facebookDateFormat )
		
		payload = \
		{
			'access_token' : accessToken,
			'since' : nowInFacebookFormat
		}
		
		response = requests.get( url, params = payload )
		return ( response.status_code, response.json() )
	
	def ProcessEvents( self, pebbleToken, events ):
		# Create parent object, this does not need to be written to the
		# database as it's only purpose is to contain the pebble token
		watch = storage.CreateWatch( pebbleToken )
		
		for event in events:
			logging.debug( "Event '" + event[ 'name' ] + "', ID: " + event[ 'id' ] )
			
			# We need to associate the key with facebook events
			key = "fbev_" + str( event[ 'id' ] )
			
			startTime = self.ISO8601ToDateTime( event[ 'start_time' ] )
			
			pin = storage.CreateWatchPin( watch, key, event[ 'name' ], event[ 'description' ], startTime )
			pin.put()
			
			#Construct HTTP put request
			pebbleDateFormat = "%Y-%m-%dT%H:%M:%S%z"
			eventTimeInPebbleFormat = self.DateTimeToPbl( startTime )
			
			body = \
			{
				'id' 		: key,
				'time' 		: eventTimeInPebbleFormat,
				'layout'	: \
				{
					'type' 		: "genericNotification",
					'title' 	: event[ 'name' ],
					'tinyIcon'	: "system://images/NOTIFICATION_FACEBOOK",
					'body' 		: event[ 'description' ]
				}
			}
			
			headers = \
			{
				'X-User-Token' : pebbleToken,
				'Content-Type' : "application/json"
			}
			
			url = "https://timeline-api.getpebble.com/v1/user/pins/" + key;
			
			#logging.debug( "Pin data: " + jsonToString( body ) )
			
			req = requests.Request( method = 'PUT', url = url, headers = headers, data = jsonToString( body ) )
			prep = req.prepare()
			
			logging.debug('{}\n{}\n{}\n\n{}'.format(
				'-----------START-----------',
				prep.method + ' ' + prep.url,
				'\n'.join('{}: {}'.format(k, v) for k, v in prep.headers.items()),
				prep.body,
			))
			
			s = requests.Session()
			response = s.send(prep)

	def GetEvents( self, pebbleToken, action ):
		# Check to see if we already have facebook access
		access = storage.FindPlatformAccessCode( pebbleToken, PLATFORM )
		
		if not access:
			response = \
			{
				'status' : "error",
				'message' : "Not authorised with facebook"
			}
			self.response.status = requests.codes.forbidden
			self.response.data = jsonToString( response )
			return
		
		status = self.NetGetEvents( access.token )
		
		if status[ 0 ] == requests.codes.ok:
			self.ProcessEvents( pebbleToken, status[ 1 ][ 'data' ] )
			self.response.status = requests.codes.ok
			
		else:
			self.response.status = requests.codes.bad_request
			self.response.data = jsonToString( status[ 1 ] )
