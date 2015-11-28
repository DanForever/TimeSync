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
import logging
from json import loads as stringToJson

#Project Imports
import common.base
import storage

class Handler( common.base.Handler ):
	def WatchInfo( self, params ):
		logging.debug( "WatchInfo(): " + str( self.request.body ) )
		
		# Convert supplied json data to usable object
		watchInfo = stringToJson( self.request.body )
		logging.debug( "WatchInfo(): " + str( watchInfo ) )
		
		# Store the data for later analysis
		storage.StoreHardwareInfo( self.request.headers[ "X-User-Token" ], watchInfo )
		
		# Standard success response
		self.response.data = { "status" : "success" }
