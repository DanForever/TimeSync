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

#Google Imports
from google.appengine.ext import db
from google.appengine.ext import blobstore

class WatchPin( db.Model ):
	title = db.StringProperty()
	body = db.StringProperty( multiline = True )
	start_time = db.DateTimeProperty()

class BetaKey( db.Model ):
	id = blobstore.BlobReferenceProperty( indexed = False )

def CreateBetaKey( key ):
	betaKey = BetaKey( key_name = "Key", id = key )
	return betaKey

def FindBetaKey():
	key = db.Key.from_path( 'BetaKey', "Key" )
	return db.get( key )

def FindChild( pebbleToken, platform, childType ):
	parentKey = db.Key.from_path( 'Watch', pebbleToken )
	key = db.Key.from_path( childType, platform, parent = parentKey )
	request = db.get( key )
	
	return request

def DeleteAllPinsForUser( pebbleToken ):
	parentKey = db.Key.from_path( 'Watch', pebbleToken )
	pins = WatchPin.all()
	pins.ancestor( parentKey )
	
	for pin in pins.run():
		pin.delete()
