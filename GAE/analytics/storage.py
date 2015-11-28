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

#Google Imports
from google.appengine.ext import db

class PebbleHardware( db.Model ):
	platform		= db.StringProperty()
	model			= db.StringProperty()
	language		= db.StringProperty()
	
	firmware_major	= db.IntegerProperty()
	firmware_minor	= db.IntegerProperty()
	firmware_patch	= db.IntegerProperty()
	firmware_suffix	= db.StringProperty()
	
	created 		= db.DateTimeProperty( auto_now_add = True )
	modified 		= db.DateTimeProperty( auto_now = True )

def StoreHardwareInfo( pebbleToken, watchInfo ):
	key = db.Key.from_path( 'PebbleHardware', pebbleToken )
	pebbleHardware = db.get( key )
	
	if( pebbleHardware is None ):
		logging.debug( "StoreHardwareInfo(): No existing PebbleHardware instance found, creating a new one!" )
		pebbleHardware = PebbleHardware( key_name = pebbleToken )
	
	logging.debug( "StoreHardwareInfo(): " + str( type( watchInfo ) ) )
	pebbleHardware.platform 		= watchInfo[ "platform" ]
	pebbleHardware.model			= watchInfo[ "model" ]
	pebbleHardware.language			= watchInfo[ "language" ]
	
	pebbleHardware.firmware_major	= watchInfo[ "firmware" ][ "major" ]
	pebbleHardware.firmware_minor	= watchInfo[ "firmware" ][ "minor" ]
	pebbleHardware.firmware_patch	= watchInfo[ "firmware" ][ "patch" ]
	pebbleHardware.firmware_suffix	= watchInfo[ "firmware" ][ "suffix" ]
	
	pebbleHardware.put()
	