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

# Google Imports
from google.appengine.ext import db

# System Imports
import logging

class TVShowtimeAgendaSubscription( db.Model ):
	created = db.DateTimeProperty( auto_now_add = True )

def StoreSubscription( pebbleToken ):
	#Create
	sub = TVShowtimeAgendaSubscription( key_name = pebbleToken )
	
	#Store
	sub.put()

def DeleteSubscription( pebbleToken ):
	#Create
	sub = TVShowtimeAgendaSubscription( pebbleToken = pebbleToken )
	
	#Store
	sub.put()

def IterateSubscriptions( callback, cursor = None ):
	
	query = TVShowtimeAgendaSubscription.all()
	
	count = 0
	batch = 1000
	
	for sub in query.run( batch_size = batch, start_cursor = cursor ):
		count = count + 1
		callback( sub )
	
	logging.info( "Completed iteration over " + str( count ) + " subscriptions" )
	
	#In the unlikely event that there are more subs to get
	if count == batch:
		IterateSubscriptions( callback, query.cursor() )

class TVShowtimeUser( db.Model ):
	id = db.IntegerProperty()
	name = db.StringProperty()

def StoreUser( pebbleToken, id, name ):
	user = TVShowtimeUser( key_name = pebbleToken, id = id, name = name )
	user.put()
	return user

def FindUser( pebbleToken ):
	key = db.Key.from_path( 'TVShowtimeUser', pebbleToken )
	request = db.get( key )
	return request