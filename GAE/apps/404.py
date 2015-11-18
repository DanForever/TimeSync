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

#System Imports
import os
from json import dumps as jsonToString

#Google Imports
import webapp2
from google.appengine.ext.webapp import template

#Library Imports
from requests import codes

class Error404Handler( webapp2.RequestHandler ):
	def get( self ):
		self.response.set_status( codes.not_found )
		self.response.write( template.render( "templates/404.html", {} ) )
		
	def post( self ):
		self.response.set_status( codes.not_found )
		self.response.write( jsonToString( { 'status' : "Invalid URL" } ) )
		self.response.headers[ "Content-Type" ] = "application/json"

app = webapp2.WSGIApplication \
(
	[
		( r'/.*', Error404Handler ),
	],
	debug = os.environ[ 'SERVER_SOFTWARE' ].startswith( 'Development' )
)
