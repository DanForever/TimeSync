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
from datetime import datetime
from json import dumps as jsonToString
import logging
import random
import string

#Library Imports
import requests

#Project Imports
import net

def AssemblePinSignature():
	firstLetter = random.SystemRandom().choice( string.ascii_uppercase )
	secondLetter = random.SystemRandom().choice( string.ascii_uppercase )
	lastNumber = random.SystemRandom().choice( string.digits )
	return "This Timeline Pin has been brought to you by time-sync.com, the letters " + firstLetter + " and " + secondLetter + ", and the number " + lastNumber

class Pin():
	def __init__( self, pebbleToken, id, time, title, icon, description = None, subtitle = None, location = None, duration = None, headings = None, paragraphs = None, source = None ):
		
		# An arbitrary, but unique string identifier (no longer than 64 characters)
		self.id 			= id
		
		# DateTime for the pin, in UTC
		self.time			= time
		
		# Title (Main text visible on the timeline
		self.title			= title
		
		# Description (Visible under more details)
		self.description	= description
		
		# Icon path that corresponds to one defined here: https://developer.getpebble.com/guides/timeline/pin-structure/#pin-icons
		self.icon			= icon
		
		# The timeline token for the pebble
		self.pebbleToken	= pebbleToken
		
		self.location = location
		self.subtitle = subtitle
		self.duration = duration
		self.source = source
		
		if headings is None:
			self.headings = []
		else:
			self.headings = headings
			
		if paragraphs is None:
			self.paragraphs = []
		else:
			self.paragraphs = paragraphs
		
		self.actions = []
	
	def AddAction( self, title, url, headers ):
		action = \
		{
			'title' : title,
			'type' : "http",
			'url' : url,
			'headers' : headers,
		}
		
		self.actions.append( action )
	
	
	
	def Send( self ):
		#Convert the python datetime object into an iso8601-ish format for the pebble api
		pebbleDateFormat = "%Y-%m-%dT%H:%M:%SZ"
		timeInPebbleFormat = self.time.strftime( pebbleDateFormat )
		
		lastUpdated = datetime.utcnow().strftime( pebbleDateFormat )
		
		if self.source is not None:
			self.headings.append( "Source" )
			self.paragraphs.append( self.source )
		
		self.headings.append( "Application" )
		self.paragraphs.append( AssemblePinSignature() )
		
		data = \
		{
			'id' 				: self.id,
			'time' 				: timeInPebbleFormat,
			'layout'			: \
			{
				'type'			: "genericPin",
				'title' 		: self.title,
				'tinyIcon'		: self.icon,
				'lastUpdated'	: lastUpdated,
				'headings'		: self.headings,
				'paragraphs'	: self.paragraphs
			}
		}
		
		if self.description is not None:
			data[ "layout" ][ "body" ] = self.description
		
		if self.subtitle is not None:
			data[ "layout" ][ "subtitle" ] = self.subtitle
		
		if self.location is not None:
			data[ "layout" ][ "locationName" ] = self.location
			data[ "layout" ][ "type" ] = "calendarPin"
		
		if self.duration is not None:
			data[ "duration" ] = self.duration
			data[ "layout" ][ "type" ] = "calendarPin"
		
		if len( self.actions ) > 0:
			data[ "actions" ] = self.actions
		
		# Construct the request config
		config = \
		{
			'request' :
			{
				'url' : "https://timeline-api.getpebble.com/v1/user/pins/" + self.id,
				'method' : "PUT",
				
				'headers' :
				{
					'X-User-Token'	: self.pebbleToken,
					'Content-Type'	: "application/json"
				},
				
				'data' : jsonToString( data )
			},
			
			'response' :
			{
				'success' :
				{
					'status' : requests.codes.ok,
					'map' : {}
				},
				
				'failure' :
				{
					'map' :
					{
						'message' : "errorCode"
					}
				}
			}
		}
		
		response = net.MakeRequest( config )
		
		return ( response[ 0 ], response[ 1 ] )