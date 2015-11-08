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

#System imports
import logging

# Library Imports
import requests

#Project imports
import base
import defines

class Handler( base.Handler ):
	def Process( self, branch, action ):
		branches = \
		{
			"auth" : self.Auth,
			"agenda" : self.Agenda,
		}
		
		actions = \
		{
			# Auth Actions
			"request" : True,
			"query"	: False,
			
			"populate": True,
		}
		
		if branch not in branches or action not in actions:
			self.response.status = requests.codes.not_found
			return
		
		pebbleToken = self.request.headers[ 'X-User-Token' ]
		
		branches[ branch ]( pebbleToken, actions[ action ] )
		
	def Auth( self, pebbleToken, action ):
		
		import auth.devices
		
		response = auth.devices.GetAccess( pebbleToken, "tvshowtime.config.auth", action )
		self.response.status = response[ 0 ]
		self.response.data = response[ 1 ]
	
	def Agenda( self, pebbleToken, action ):
		import storage
		import net
		import config.agenda

		platformAccess = storage.FindPlatformAccessCode( pebbleToken, defines.PLATFORM )
		
		if platformAccess is None:
			self.response.status = requests.codes.unauthorized
			return
		
		db = \
		{
			'access_token' : platformAccess.token
		}
		
		logging.debug( "DB: " + str( db ) )
		response = net.MakeRequest( config.agenda.CONFIG, db )
		
		for episode in response[ 1 ][ "episodes" ]:
			logging.debug( "Show: " + episode[ "show" ][ "name" ] );
			logging.debug( "Network: " + episode[ "network" ] );
			logging.debug( "Name: " + episode[ "name" ] );
			logging.debug( "Airs: " + episode[ "air_date" ] );
			logging.debug( "Id: " + str( episode[ "id" ] ) );
			logging.debug( "EpNum: " + str( episode[ "season_number" ] ) + "x" + str( episode[ "number" ] ) );
		
		self.response.status = response[ 0 ]
		