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

class Watch( db.Model ):
	blarg = db.StringProperty()

class PlatformAuthRequest( db.Model ):
	# Internal code used to verify authorisation with platform
	auth_code = db.StringProperty( indexed = False )
	
	# Code displayed to the user that they have to manually enter into platform website
	user_code = db.StringProperty( indexed = False )
	
	# URL the user must go to in order to enter the user_code and authorise their pebble
	user_uri = db.LinkProperty( indexed = False )
	
	# Expire time
	expires = db.DateTimeProperty()
	
	# Expire time
	update_interval = db.IntegerProperty( indexed = False )

class PlatformAccess( db.Model ):
	token = db.StringProperty( indexed = False )

def CreateWatch( access_token ):
	watch = Watch( key_name = access_token )
	return watch

def CreatePlatformAuthRequest( watch, platform, private_key, public_key, url, expires, interval ):
	
	request = PlatformAuthRequest \
	(
		# Parent Is always the watch
		parent = watch,
		
		# Key is the platform - there's only ever one entry per watch per platform
		key_name = platform,
		
		# Auth request data
		auth_code = private_key,
		user_code = public_key,
		user_uri = url,
		expires = expires,
		update_interval = interval
	)
	
	return request

def CreateAccess( watch, platform, platform_token ):
	
	access = PlatformAccess \
	(
		# Parent Is always the watch
		parent = watch,
		
		# Key is the platform - there's only ever one entry per watch per platform
		key_name = platform,
		
		# The code that gives us access to this user's facebook data
		token = platform_token
	)
	
	return access

def FindChild( pebbleToken, platform, childType ):
	parentKey = db.Key.from_path( 'Watch', pebbleToken )
	key = db.Key.from_path( childType, platform, parent = parentKey )
	request = db.get( key )
	
	return request

def FindPlatformAuthRequest( pebbleToken, platform ):
	return FindChild( pebbleToken, platform, 'PlatformAuthRequest' )

def FindPlatformAccessCode( pebbleToken, platform ):
	return FindChild( pebbleToken, platform, 'PlatformAccess' )
