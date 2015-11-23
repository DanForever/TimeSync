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

class FacebookSubscription( db.Model ):
	watchToken = db.StringProperty()
	events = db.BooleanProperty()
	created = db.DateTimeProperty( auto_now_add = True )

class TemporaryAuthToken( db.Model ):
	token = db.StringProperty()

class FacebookUser( db.Model ):
	name = db.StringProperty()

def CreateTemporaryAuthToken( token, generatedToken ):
	token = TemporaryAuthToken( key_name = generatedToken, token = token )
	return token

def CreateFacebookSubscription( fbuid, pebbleToken ):
	entry = FacebookSubscription \
	(
		key_name = fbuid,
		watchToken = pebbleToken,
		events = False,
		birthdays = False
	)
	
	return entry

def CreateUser( pebbleToken, name ):
	user = FacebookUser \
	(
		key_name = pebbleToken,
		name = name
	)
	
	return user

def FindTemporaryAuthToken( token ):
	key = db.Key.from_path( 'TemporaryAuthToken', token )
	return db.get( key )

def FindFacebookSubscriptionByWatchToken( pebbleToken ):
	query = FacebookSubscription.all()
	query.filter( "watchToken =", pebbleToken )
	return query.get()
	
def FindFacebookSubscription( fbuid ):
	key = db.Key.from_path( 'FacebookSubscription', fbuid )
	return db.get( key )

def FindUser( pebbleToken ):
	key = db.Key.from_path( 'FacebookUser', pebbleToken )
	return db.get( key )
