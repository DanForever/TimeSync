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
		
class DateLineGraphDataset():
	def __init__( self, name = "" ):
		self.dates = {}
		self.earliestDate = datetime.date.today()
		
		self.labels					= ""
		self.name					= name
		self.fillColor				= "rgba(220,220,220,0.2)"
		self.strokeColor			= "rgba(220,220,220,1)"
		self.pointColor				= "rgba(220,220,220,1)"
		self.pointStrokeColor		= "#fff"
		self.pointHighlightFill		= "#fff"
		self.pointHighlightStroke	= "rgba(220,220,220,1)"
	
	def NumberOfDays( self ):
		return ( datetime.date.today() - self.earliestDate ).days
	
	def Get( self, date ):
		return self.dates.get( date, 0 )
		
	def Add( self, date ):
		value = self.Get( date )
		self.dates[ date ] = value + 1
		
		if date < self.earliestDate:
			self.earliestDate = date
			
	def GetStringForRange( self, numberOfDays ):
	
		oneDay = datetime.timedelta( days = 1 )
		
		dayCount = min( numberOfDays, self.NumberOfDays() )
		currentDay = datetime.date.today() - datetime.timedelta( days = dayCount )
		
		values = ""
		self.labels = ""
		for x in xrange( dayCount ):
			logging.debug( str( x ) + ") Adding " + str( currentDay ) + " to graph" )
			
			if x > 0:
				values += ","
				self.labels += ","
			
			value = self.Get( currentDay )
			values += str( value )
			self.labels += "\"" + str( currentDay ) + "\""
			currentDay += oneDay
		
		datasetString = \
		'label: "{0.name}",\n'\
		'fillColor: "{0.fillColor}",\n'\
		'strokeColor: "{0.strokeColor}",\n'\
		'pointColor: "{0.pointColor}",\n'\
		'pointStrokeColor: "{0.pointStrokeColor}",\n'\
		'pointHighlightFill: "{0.pointHighlightFill}",\n'\
		'pointHighlightStroke: "{0.pointHighlightStroke}",\n'\
		'data: [{1}]'
		
		return "{" + datasetString.format( self, values ) + "}"

class Handler( common.base.Handler ):
	def __init__( self, app, request ):
		common.base.Handler.__init__( self, app, request )
		self.charts = []
		
		self.pebbleTokens = []
		self.facebookSubscriptionCount = 0
		self.tvshowtimeSubscriptionCount = 0
		
	def AnalyseData( self ):
		#Create Data
		self.installs = DateLineGraphDataset( "New unique installs" )
		self.facebookSubscriptions = DateLineGraphDataset( "Facebook subscriptions" )
		self.tvshowtimeSubscriptions = DateLineGraphDataset( "TVShow Time subscriptions" )
	
		#Analyse
		self.AnalyseFacebookSubscriptions()
		self.AnalyseTVShowtimeSubscriptions()

		self.uniquePebbleTokens = set( self.pebbleTokens )
		self.crossSubscribers = len( self.pebbleTokens ) - len( self.uniquePebbleTokens )
		
		analytics.storage.IterateHardwareInfo( self.AnalyseHardwareItem )

	def AnalyseHardwareItem( self, item ):
		self.installs.Add( item.created.date() )
	
	def AnalyseFacebookSubscriptions( self ):
		query = facebook.storage.FacebookSubscription.all()
		for sub in query.run( limit = 1000 ):
			if sub.events:
				self.facebookSubscriptionCount += 1
				self.pebbleTokens.append( sub.watchToken )
			if sub.created is not None:
				self.facebookSubscriptions.Add( sub.created.date() )

	def AnalyseTVShowtimeSubscriptions( self ):
		query = tvshowtime.storage.TVShowtimeAgendaSubscription.all()
		for sub in query.run( limit = 1000 ):
			self.tvshowtimeSubscriptionCount += 1
			self.pebbleTokens.append( sub.key().name() )
			self.tvshowtimeSubscriptions.Add( sub.created.date() )
	
	def CreateSubscriptionChart( self ):
		
		users = Chart( "Active subscriptions" )
		users.AddSection( self.facebookSubscriptionCount - self.crossSubscribers, "#3b5999", "#4B70BF", "Facebook Events" )
		users.AddSection( self.tvshowtimeSubscriptionCount - self.crossSubscribers, "#F0F011", "#FFFF00", "TVShow Time" )
		users.AddSection( self.crossSubscribers, "#72DB76", "#7FEB82", "Both" )
		users.GenerateJavascript()
		
		js = 'Chart.defaults.global.legendTemplate = "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<segments.length; i++){%><li><span style=\"-moz-border-radius:7px 7px 7px 7px; border-radius:7px 7px 7px 7px; margin-right:10px;width:15px;height:15px;display:inline-block;background-color:<%=segments[i].fillColor%>\"> </span><%if(segments[i].label){%><%=s egments[i].label%><%}%></li><%}%></ul>";'
		
		self.charts.append \
		(
			{
				'id' : users.id,
				'javascript' : users.javascript,
				'width' : 250,
				'height' : 250
			}
		)
		
	def CreateDateGraph( self ):
		
		self.facebookSubscriptions.fillColor				= "rgba(59,89,153,0.2)"
		self.facebookSubscriptions.strokeColor				= "rgba(59,89,153,1)"
		self.facebookSubscriptions.pointColor				= "rgba(59,89,153,1)"
		self.facebookSubscriptions.pointStrokeColor			= "#fff"
		self.facebookSubscriptions.pointHighlightFill		= "#fff"
		self.facebookSubscriptions.pointHighlightStroke		= "rgba(59,89,153,1)"
		
		self.tvshowtimeSubscriptions.fillColor				= "rgba(240,240,17,0.2)"
		self.tvshowtimeSubscriptions.strokeColor			= "rgba(240,240,17,1)"
		self.tvshowtimeSubscriptions.pointColor				= "rgba(240,240,17,1)"
		self.tvshowtimeSubscriptions.pointStrokeColor		= "#fff"
		self.tvshowtimeSubscriptions.pointHighlightFill		= "#fff"
		self.tvshowtimeSubscriptions.pointHighlightStroke	= "rgba(240,240,17,1)"
		
		# Previous week
		numberOfDaysToDisplay = 14
		
		datasets = \
		[
			self.installs.GetStringForRange( numberOfDaysToDisplay ),
			self.facebookSubscriptions.GetStringForRange( numberOfDaysToDisplay ),
			self.tvshowtimeSubscriptions.GetStringForRange( numberOfDaysToDisplay )
		]
		
		data = \
		{
			'id' : "installs_id",
			'labels' : self.installs.labels,
			'datasets' : ",".join( datasets )
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

	def Main( self, params ):
		
		self.AnalyseData()
		self.CreateSubscriptionChart()
		self.CreateDateGraph()
		
		data = \
		{
			'charts' : self.charts
		}
		
		self.response.data = template.render( "templates/admin/analytics.html", data )
