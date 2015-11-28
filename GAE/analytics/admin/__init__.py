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
from google.appengine.ext.webapp import template

#Project Imports
import common.base

import facebook.storage
import tvshowtime.storage

class Chart():
	id = 0
	def __init__( self, name ):
		self.name = name
		self.sections = []
		self.id = "chartsection" + str( Chart.id )
		Chart.id = Chart.id + 1
		
	def AddSection( self, value, colour, highlight, name ):
		section = \
		{
			'value' : value,
			'colour' : colour,
			'highlight' : highlight,
			'name' : name,
		}
		
		self.sections.append( section )
		
	def GenerateJavascript( self ):
		
		data = \
		{
			'id' : self.id,
			'name' : self.name,
			'sections' : self.sections,
		}
		
		self.javascript = template.render( "templates/admin/chart.js", data )

def CountFacebookSubscriptions( pebbleTokens ):
	count = 0
	query = facebook.storage.FacebookSubscription.all()
	for sub in query.run( limit = 1000 ):
		if sub.events:
			count = count + 1
			pebbleTokens.append( sub.watchToken )
	return count
	
def CountTVShowtimeSubscriptions( pebbleTokens ):
	count = 0
	query = tvshowtime.storage.TVShowtimeAgendaSubscription.all()
	for sub in query.run( keys_only = True, limit = 1000 ):
		count = count + 1
		pebbleTokens.append( sub.name() )
	return count

class Handler( common.base.Handler ):
	def Main( self, params ):
		
		pebbleTokens = []
		facebookSubs = CountFacebookSubscriptions( pebbleTokens )
		tvshowtimeSubs = CountTVShowtimeSubscriptions( pebbleTokens )
		uniquePebbleTokens = set( pebbleTokens )
		crossSubscribers = len( pebbleTokens ) - len( uniquePebbleTokens )
		
		users = Chart( "Active subscriptions" )
		users.AddSection( facebookSubs - crossSubscribers, "#3b5999", "#4B70BF", "Facebook Events" )
		users.AddSection( tvshowtimeSubs - crossSubscribers, "#F0F011", "#FFFF00", "TVShow Time" )
		users.AddSection( crossSubscribers, "#72DB76", "#7FEB82", "Both" )
		users.GenerateJavascript()
		
		data = \
		{
			'charts' :
			[
				{
					'id' : users.id,
					'javascript' : users.javascript
				}
			]
		}
		
		self.response.data = template.render( "templates/admin/analytics.html", data )