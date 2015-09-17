import webapp2
import json

class Handler(webapp2.RequestHandler):
	def post(self, branch):
		
		options = \
		{
			"subscribe" : Subscribe
		}
		
		#output = options[ branch ](  )
		
		payload = json.loads( str( self.request.body ) )
		
		self.response.write( "Token from Json: " + payload['token'] + "\n" )
		self.response.write( "Token from header: " + self.request.headers[ 'X-User-Token' ] + "\n" )
		self.response.write( "\n" )
		self.response.write( "Timeline token: " + str( payload ) + "\n" )
		self.response.write( "Headers: " + str( self.request.headers ) + "\n" )

def Subscribe( postData ):
	return postData

def GetTimelineToken( requestData ):
	pass