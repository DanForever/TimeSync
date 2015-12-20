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

#System Imports
import logging

# Project Imports
import common.datetime

class TimelinePin( db.Model ):
	created		= db.DateTimeProperty( auto_now_add = True )
	
	time		= db.DateTimeProperty()
	
	title		= db.IntegerProperty( indexed = False )
	description	= db.IntegerProperty( indexed = False )
	location	= db.IntegerProperty( indexed = False )
	subtitle	= db.IntegerProperty( indexed = False )
	duration	= db.IntegerProperty( indexed = False )
	source		= db.IntegerProperty( indexed = False )
	
	headings	= db.ListProperty( int, indexed = False )
	paragraphs	= db.ListProperty( int, indexed = False )

	def MakeTimeAware( self ):
		if self.time.tzinfo is None or self.time.tzinfo.utcoffset( self.time ):
			self.time = self.time.replace( tzinfo = common.datetime.UTC )
	
	def IsEqualTo( self, other ):
		#This exists because google app engine stores datetimes as UTC and timezone naive
		self.MakeTimeAware()
		other.MakeTimeAware()
		
		if self.time != other.time:
			logging.debug( "Time has changed" )
			return False
		
		if self.title != other.title:
			logging.debug( "Title has changed" )
			return False
		
		if self.description != other.description:
			logging.debug( "Description has changed" )
			return False
		
		if self.location != other.location:
			logging.debug( "Location has changed" )
			return False
		
		if self.subtitle != other.subtitle:
			logging.debug( "Subtitle has changed" )
			return False
		
		if self.duration != other.duration:
			logging.debug( "Duration has changed" )
			return False
		
		if self.source != other.source:
			logging.debug( "Source has changed" )
			return False
		
		if cmp( self.headings, other.headings ) != 0:
			logging.debug( "Headings have changed" )
			return False
		
		if cmp( self.paragraphs, other.paragraphs ) != 0:
			logging.debug( "Paragraphs have changed" )
			return False
		
		return True

def CreateTimelinePin( id, **values ):
	pin = TimelinePin( key_name = id, **values )
	return pin
	
def FindTimelinePin( id ):
	key = db.Key.from_path( 'TimelinePin', id )
	return db.get( key )
