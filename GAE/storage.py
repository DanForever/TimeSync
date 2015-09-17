from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.ext import blobstore

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

class BetaKey( db.Model ):
	id = blobstore.BlobReferenceProperty()

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

def FindBetaKey():
	key = db.Key.from_path( 'BetaKey', "Key" )
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
