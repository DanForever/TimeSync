import requests
import webapp2
import storage
import datetime
from json import dumps as jsonToString
from json import loads as stringToJson
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

class BaseHandler():
	def __init__( self, app, request ):
		self.response = HTTPResponse()
		self.app = app
		self.request = request

class CallbackHandler( BaseHandler ):
	def Get( self ):
		logging.debug( "Facebook callback handler Get(): " + str( self.request.GET ) )

		if not ( self.request.GET[ 'hub.mode' ] == "subscribe" ):
			logging.debug( "Facebook callback handler Get(): Missing subcribe mode" )
			self.response.status = requests.codes.bad_request
			return
		
		storedToken = storage.FindTemporaryAuthToken( self.request.GET[ 'hub.verify_token' ] )
		
		if not storedToken:
			logging.debug( "Facebook Missing storage token" )
			self.response.status = requests.codes.unauthorized
			return
		
		pebbleToken = storedToken.watchToken
		storedToken.delete()
		
		self.response.status = requests.codes.ok
		self.response.data = self.request.GET[ 'hub.challenge' ]
	
	def Post( self ):
		logging.debug( "CallbackHandler Post()" )
		logging.debug( "Callback headers: " + str( self.request.headers ) )
		logging.debug( "Callback POST: " + str( self.request.POST ) )
		logging.debug( "Callback body: " + str( self.request.body ) )
		
		# First authenticate that the request was made by facebook
		import hmac
		import hashlib
		
		calculatedSha = "sha1=" + hmac.new( secrets.facebook.APP_SECRET, str( self.request.body ), hashlib.sha1 ).hexdigest()
		receivedSha = self.request.headers[ 'X-Hub-Signature' ]
		
		if calculatedSha == receivedSha:
			logging.debug( "Calculated SHA (" + calculatedSha + ") matches received SHA" )
			
			requestData = stringToJson( self.request.body )
			
			if requestData[ 'object' ] == "user":
				for entry in requestData[ 'entry' ]:
					if "events" in entry[ 'changed_fields' ]:
						fbuid = entry[ 'uid' ]
						
						logging.debug( "Checking subscription data for user: " + str( fbuid ) )
						fbSub = storage.FindFacebookSubscription( fbuid )
						
						if fbSub.events:
							logging.debug( "Updating events for user: " + str( fbuid ) )
							
							regularHandler = Handler( self.app, self.request )
							regularHandler.GetEvents( fbSub.watchToken )
			
			self.response.status = requests.codes.ok
		
		else:
			self.response.status = requests.codes.unauthorized
			
class Handler( BaseHandler ):
	def Process( self, branch, action ):
		branches = \
		{
			"auth" : self.GetAccess,
			"events" : self.SubscribeEvents,
			"birthdays" : self.SubscribeBirthdays
		}
		
		actions = \
		{
			"subscribe" : True,
			"unsubscribe" : False,
			
			# Auth Actions
			"request" : True,
			"query"	: False
		}
		
		if branch not in branches or action not in actions:
			self.response.status = requests.codes.not_found
			return
		
		pebbleToken = self.request.headers[ 'X-User-Token' ]
		
		branches[ branch ]( pebbleToken, actions[ action ] )

	def SubscribeEvents( self, pebbleToken, action ):
		logging.debug( "SubscribeEvents()" )
		
		# update sub data
		fbSubData = storage.FindFacebookSubscriptionByWatchToken( pebbleToken )
		fbSubData.events = action
		fbSubData.put()
		
		if action:
			# Grab all the events for the user
			self.GetEvents( pebbleToken )
		
		response = \
		{
			'status' : "success",
		}
		self.response.status = requests.codes.ok
		self.response.data = jsonToString( response )
		
	def SubscribeBirthdays( self, pebbleToken, action ):
		logging.debug( "SubscribeBirthdays()" )
		
		# update sub data
		fbSubData = storage.FindFacebookSubscriptionByWatchToken( pebbleToken )
		fbSubData.birthdays = action
		fbSubData.put()
		
		response = \
		{
			'status' : "success",
		}
		self.response.status = requests.codes.ok
		self.response.data = jsonToString( response )
		
	def Subscribe( self, pebbleToken, type ):
		logging.debug( "Facebook Subscribe()" )
		
		callbackUrl = self.app.router.build \
		(
			self.request,
			"callback",
			(),
			{
				'version' : 1,
				'handler' : "facebook",
				'_full' : True,
				'_scheme' : "https"
			}
		)
		
		logging.debug( "callback url: " + callbackUrl )
		
		import random
		import string
		authToken = ''.join( random.SystemRandom().choice( string.ascii_uppercase + string.digits ) for _ in range( 10 ) )
		
		tokenStorage = storage.CreateTemporaryAuthToken( pebbleToken, authToken )
		tokenStorage.put()
		
		payload = \
		{
			'object' : "user",
			'fields' : type,
			'callback_url' : callbackUrl,
			'verify_token' : authToken,
			'access_token' : str( secrets.facebook.CLIENT_ID ) + "|" + secrets.facebook.APP_SECRET
		}
		
		url = "https://graph.facebook.com/v2.4/" + str( secrets.facebook.CLIENT_ID ) + "/subscriptions"
		
		response = requests.post( url, params = payload )
		
		self.response.status = response.status_code
		self.response.data = response.text
	
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
		loginCodeStatus = self.NetGetDeviceLoginCodeStatus( authRequest.auth_code )
		
		if loginCodeStatus[ 0 ] == requests.codes.ok:
			# Create parent object, this does not need to be written to the
			# database as it's only purpose is to contain the pebble token
			watch = storage.CreateWatch( pebbleToken )
			
			accessToken = loginCodeStatus[ 1 ][ 'access_token' ]
			access = storage.CreateAccess( watch, PLATFORM, accessToken )
			
			# store it in the database
			access.put()
			
			# We need to store the facebook user id for when we're told about event changes
			# And also the user's name so that we can display it on the watch as evidence of a successful sign in
			getDataStatus = self.NetGetCurrentUserData( accessToken )
			
			if( getDataStatus[ 0 ] == requests.codes.ok ):
				
				self.response.status = requests.codes.ok
				
				response = \
				{
					'status' : "success",
					'name' : getDataStatus[ 1 ][ 'name' ]
				}
				
				newSub = storage.CreateFacebookSubscription( getDataStatus[ 1 ][ 'id' ], pebbleToken )
				newSub.put()
				
				# No longer required
				authRequest.delete()
				
			else:
				self.response.status = requests.codes.bad_request
				response = \
				{
					'status' : "failure",
					'message' : "Could not get user details",
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
		
	def NetGetCurrentUserData( self, accessToken ):
		url = "https://graph.facebook.com/v2.4/me"
		
		payload = \
		{
			'access_token' : accessToken,
		}
		
		response = requests.get( url, params = payload )
		return ( response.status_code, response.json() )
		
	def NetGetEvents( self, accessToken ):
		url = "https://graph.facebook.com/v2.4/me/events"
		
		# Since the timeline can't be populated with anything older than 2 days ago
		# We limit the query to recent and future events
		since = datetime.datetime.now( UTC() ) - datetime.timedelta( days = 2 )
		
		nowInFacebookFormat = self.DateTimeToISO8601( since )
		
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
			
			if 'description' in event:
				description = event[ 'description' ]
			else:
				description = "No description"
			
			pin = storage.CreateWatchPin( watch, key, event[ 'name' ], description, startTime )
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
					'body' 		: description
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
			
			logging.debug( "Pin response status: " + str( response.status_code ) )
			logging.debug( "Pin response data: " + response.text )

	def GetEvents( self, pebbleToken ):
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
			return True
			
		else:
			return False
