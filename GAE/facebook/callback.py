
#System imports
import logging

from json import loads as stringToJson

#Library imports
import requests

#Project imports
import base
import secrets.facebook
import storage
import defines
import events

class Handler( base.Handler ):
	def Get( self ):
		logging.debug( "Facebook callback handler Get(): " + str( self.request.GET ) )

		if not ( self.request.GET[ 'hub.mode' ] == "subscribe" ):
			logging.debug( "Facebook callback handler Get(): Missing subcribe mode" )
			self.response.status = requests.codes.bad_request
			return
		
		if 'hub.verify_token' not in self.request.GET:
			logging.debug( "Facebook callback handler Get(): Missing verify_token" )
			self.response.status = requests.codes.bad_request
			return
		
		storedToken = storage.FindTemporaryAuthToken( self.request.GET[ 'hub.verify_token' ] )
		
		if not storedToken:
			logging.debug( "Facebook Missing storage token" )
			self.response.status = requests.codes.unauthorized
			return
		
		token = storedToken.token
		storedToken.delete()
		
		if token == defines.SUBSCRIBE_HANDSHAKE_TOKEN:
			self.response.status = requests.codes.ok
			self.response.data = self.request.GET[ 'hub.challenge' ]
		else:
			logging.debug( "Facebook callback handler Get(): Retrieved token does not match expected token" )
			self.response.status = requests.codes.unauthorized
	
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
							
							events.Fetch( fbSub.watchToken, fbuid )
			
			self.response.status = requests.codes.ok
		
		else:
			self.response.status = requests.codes.unauthorized