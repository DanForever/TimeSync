
import requests

class HTTPResponse():
	def __init__( self ):
		self.status = requests.codes.ok
		self.data = ""

class Handler():
	def __init__( self, app, request ):
		self.response = HTTPResponse()
		self.app = app
		self.request = request