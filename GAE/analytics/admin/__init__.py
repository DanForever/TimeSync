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
import datetime

#Google Imports
from google.appengine.ext.webapp import template

#Project Imports
import common.base

import facebook.storage
import tvshowtime.storage
import analytics.storage

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

class DateLineGraphDataset():
	def __init__( self ):
		self.dates = {}
		self.earliestDate = datetime.date.today()
	
	def NumberOfDays( self ):
		return ( datetime.date.today() - self.earliestDate ).days
	
	def Get( self, date ):
		return self.dates.get( date, 0 )
		
	def Add( self, date ):
		value = self.Get( date )
		self.dates[ date ] = value + 1
		
		if date < self.earliestDate:
			self.earliestDate = date

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
	def __init__( self, app, request ):
		common.base.Handler.__init__( self, app, request )
		self.charts = []
		
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
		
		self.charts.append \
		(
			{
				'id' : users.id,
				'javascript' : users.javascript,
				'width' : 250,
				'height' : 250
			}
		)
		
		self.AnalyseHardware()
		
		data = \
		{
			'charts' : self.charts
		}
		
		self.response.data = template.render( "templates/admin/analytics.html", data )
		
	def AnalyseHardware( self ):
		self.installs = DateLineGraphDataset()
		analytics.storage.IterateHardwareInfo( self.AnalyseHardwareItem )
		
		dayCount = self.installs.NumberOfDays()
		oneDay = datetime.timedelta( days = 1 )
		currentDay = self.installs.earliestDate
		
		logging.debug( "earliestDate: " + str( self.installs.earliestDate ) + " " + str( type( self.installs.earliestDate ) ) )
		logging.debug( "oneDay: " + str( oneDay ) + " " + str( type( oneDay ) ) )
		logging.debug( "Daycount: " + str( dayCount ) + " " + str( type( dayCount ) ) )
		
		#labels: ["January", "February", "March", "April", "May", "June", "July"],
		#datasets: [
		#	{
		#		label: "My First dataset",
		#		fillColor: "rgba(220,220,220,0.2)",
		#		strokeColor: "rgba(220,220,220,1)",
		#		pointColor: "rgba(220,220,220,1)",
		#		pointStrokeColor: "#fff",
		#		pointHighlightFill: "#fff",
		#		pointHighlightStroke: "rgba(220,220,220,1)",
		#		data: [65, 59, 80, 81, 56, 55, 40]
		#	},
		
		labels = ""
		values = ""
		for x in xrange( dayCount ):
			logging.debug( "Adding " + str( currentDay ) + " to graph" )
			
			if x > 0:
				labels += ","
				values += ","
			
			value = self.installs.Get( currentDay )
			labels += "\"" + str( currentDay ) + "\""
			values += str( value )
			currentDay += oneDay
		
		dataset = \
		'{label: "My First dataset",\n'\
		'fillColor: "rgba(220,220,220,0.2)",\n'\
		'strokeColor: "rgba(220,220,220,1)",\n'\
		'pointColor: "rgba(220,220,220,1)",\n'\
		'pointStrokeColor: "#fff",\n'\
		'pointHighlightFill: "#fff",\n'\
		'pointHighlightStroke: "rgba(220,220,220,1)",\n'\
		'data: [' + values + ']}'
		
		data = \
		{
			'id' : "installs_id",
			'labels' : labels,
			'datasets' : dataset
		}
		
		javascript = template.render( "templates/admin/linegraph.js", data )
		
		self.charts.append \
		(
			{
				'id' : "installs_id",
				'javascript' : javascript,
				'width' : 800,
				'height' : 250
			}
		)

	def AnalyseHardwareItem( self, item ):
		logging.debug( "AnalyseHardwareItem()" )
		self.installs.Add( item.created.date() )