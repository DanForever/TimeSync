
#system imports
import datetime

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
	
	response = requests.post( URL_BASE + URL_SUB_AUTH, params = payload )
	
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