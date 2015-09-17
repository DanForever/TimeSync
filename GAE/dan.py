
import requests

def FetchAuth():
	baseUrl = 'https://graph.facebook.com/'
	subUrl = 'oauth/device'
	
	payload = \
	{
		'type' : 'device_code',
		'client_id' : 467075373468891,
		'scope' : 'user_events'
	}
	
	response = requests.post( baseUrl + subUrl, params = payload )
	
	return response.text

def stuff():
	try:
		return FetchAuth()
	except requests.exceptions.RequestException as e:
		return str( e )