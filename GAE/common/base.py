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

#Library Imports
import requests

#Project Imports
import auth.storage
import auth.keys

class HTTPResponse():
	def __init__( self ):
		self.status = requests.codes.ok
		self.data = ""

class Handler():
	def __init__( self, app, request ):
		self.response = HTTPResponse()
		self.app = app
		self.request = request
		
	def CreateConfigDB( self, platform, pebbleToken = None, platformAccess = None ):
		
		if pebbleToken == None:
			if "X-User-Token" in self.request.headers:
				pebbleToken = self.request.headers[ "X-User-Token" ]
		
		if platformAccess is None:
			platformAccess = auth.storage.FindPlatformAccessCode( pebbleToken, platform )
			if platformAccess is None:
				return None
		
		db = \
		{
			auth.keys.ACCESS_TOKEN_KEY : platformAccess.token
		}
		
		return db
		
	def GetUrl( self, handler, params, full = True, scheme = "https" ):
		
		params[ "version" ]	= 1
		params[ "_full" ]	= full
		params[ "_scheme" ] = scheme
		
		url = self.app.router.build \
		(
			self.request,
			handler,
			(),
			params
		)
		
		return url