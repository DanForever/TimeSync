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
from google.appengine.ext.db import polymodel
from google.appengine.ext import blobstore

#System Imports
import logging

#A data descriptor that sets and returns values normally and prints a message logging their access.
class RevealAccess(object):
	def __init__( self, value ):
		self.val = value
	def __get__( self, obj, objtype ):
		return self.val
	def __set__( self, obj, val ):
		pass

class Watch( db.Model ):
	blarg = db.StringProperty()

class PlatformAuthRequest( db.Model ):
	# Internal code used to verify authorisation with platform
	auth_code = db.StringProperty()
	
	# Code displayed to the user that they have to manually enter into platform website
	user_code = db.StringProperty()
	
	# URL the user must go to in order to enter the user_code and authorise their pebble
	user_uri = db.LinkProperty()
	
	# Expire time
	expires = db.DateTimeProperty()
	
	# Expire time
	update_interval = db.IntegerProperty()

class PlatformAccess( db.Model ):
	token = db.StringProperty()

class WatchPin( db.Model ):
	title = db.StringProperty()
	body = db.StringProperty( multiline = True )
	start_time = db.DateTimeProperty()

class FacebookSubscription( db.Model ):
	watchToken = db.StringProperty()
	events = db.BooleanProperty()
	birthdays = db.BooleanProperty()

class BetaKey( db.Model ):
	id = blobstore.BlobReferenceProperty()

class TemporaryAuthToken( db.Model ):
	token = db.StringProperty()

def CreateTemporaryAuthToken( token, generatedToken ):
	token = TemporaryAuthToken( key_name = generatedToken, token = token )
	return token

def CreateFacebookSubscription( fbuid, watchToken ):
	entry = FacebookSubscription \
	(
		key_name = fbuid,
		watchToken = watchToken,
		events = False,
		birthdays = False
	)
	
	return entry

def CreateBetaKey( key ):
	betaKey = BetaKey( key_name = "Key", id = key )
	return betaKey

def CreateWatch( access_token ):
	watch = Watch( key_name = access_token )
	
	return watch

def CreatePlatformAuthRequest( watch, platform, auth_code, user_code, user_uri, expires, update_interval ):
	
	request = PlatformAuthRequest \
	(
		# Parent Is always the watch
		parent = watch,
		
		# Key is the platform - there's only ever one entry per watch per platform
		key_name = platform,
		
		# Auth request data
		auth_code = auth_code,
		user_code = user_code,
		user_uri = user_uri,
		expires = expires,
		update_interval = update_interval
	)
	
	return request

def CreateAccess( watch, platform, access_token ):
	
	access = PlatformAccess \
	(
		# Parent Is always the watch
		parent = watch,
		
		# Key is the platform - there's only ever one entry per watch per platform
		key_name = platform,
		
		# The code that gives us access to this user's facebook data
		token = access_token
	)
	
	return access

def CreateWatchPin( watch, id, title, body, start_time ):
	
	pin = WatchPin \
	(
		parent = watch,
		
		key_name = id,
		
		title = title,
		body = body,
		start_time = start_time
	)
	
	return pin

def FindTemporaryAuthToken( token ):
	key = db.Key.from_path( 'TemporaryAuthToken', token )
	return db.get( key )

def FindBetaKey():
	key = db.Key.from_path( 'BetaKey', "Key" )
	return db.get( key )

def FindFacebookSubscriptionByWatchToken( watchToken ):
	query = FacebookSubscription.all()
	query.filter( "watchToken =", watchToken )
	return query.get()
	
def FindFacebookSubscription( fbuid ):
	key = db.Key.from_path( 'FacebookSubscription', fbuid )
	return db.get( key )
	
def FindChild( pebbleToken, platform, childType ):
	parentKey = db.Key.from_path( 'Watch', pebbleToken )
	key = db.Key.from_path( childType, platform, parent = parentKey )
	request = db.get( key )
	
	return request

def FindPlatformAuthRequest( pebbleToken, platform ):
	return FindChild( pebbleToken, platform, 'PlatformAuthRequest' )

def FindPlatformAccessCode( pebbleToken, platform ):
	return FindChild( pebbleToken, platform, 'PlatformAccess' )
	
def DeleteAllPinsForUser( pebbleToken ):
	logging.debug( "DeleteAllPinsForUser()" )
	
	parentKey = db.Key.from_path( 'Watch', pebbleToken )
	pins = WatchPin.all()
	pins.ancestor( parentKey )
	
	for pin in pins.run():
		pin.delete()
