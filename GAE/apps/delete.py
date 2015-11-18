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

#Library Imports
from requests import codes

#Project Imports
import base
import common.storage

class DeleteHandler( base.Handler ):
	def common( self, params, method ):
		
		if method != "delete":
			self.response.set_status( codes.file_not_found )
			return
		
		if 'X-User-Token' not in self.request.headers:
			self.response.set_status( codes.unauthorized )
			return
		
		common.storage.DeleteAllPinsForUser( self.request.headers[ 'X-User-Token' ] )
		
		response = jsonToString( { 'status' : "success" } )
		self.response.set_status( codes.ok )
		self.response.write( response )
		self.response.headers[ "Content-Type" ] = "application/json"

app = webapp2.WSGIApplication \
(
	[
		webapp2.Route( '/delete/v<version:\d+>/', DeleteHandler ),
	],
	debug = os.environ[ 'SERVER_SOFTWARE' ].startswith( 'Development' )
)

