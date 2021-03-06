#!/usr/bin/python
# -*- coding: utf-8 -*-

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

#Imports from the future!
from __future__ import unicode_literals

#System Imports
from datetime import datetime
from json import dumps as jsonToString
import logging
import random
import string
import zlib

#Library Imports
from requests import codes

#Project Imports
import net
import common.datetime
import storage

def AssemblePinSignature():
	firstLetter = random.SystemRandom().choice( string.ascii_uppercase )
	secondLetter = random.SystemRandom().choice( string.ascii_uppercase )
	lastNumber = random.SystemRandom().choice( string.digits )
	return "This Timeline Pin has been brought to you by time-sync.com, the letters " + firstLetter + " and " + secondLetter + ", and the number " + lastNumber

def Sanitise( input, maxLength ):
	if input is not None:
		if len( input ) > maxLength:
			input = input[ : maxLength - 3 ] + "..."
	return input

def CalcHash( data ):
	if data is None:
		return 0
	if isinstance( data, unicode ):
		logging.debug( "Data is unicode, converting: " + data )
		data = jsonToString( data )
		logging.debug( "Data is json: " + data )
	return zlib.adler32( data )

class Pin():
	def __init__( self, pebbleToken, id, time, title, icon, description = None, subtitle = None, location = None, duration = None, headings = None, paragraphs = None, source = None ):

		# An arbitrary, but unique string identifier (no longer than 64 characters)
		self.id 			= id

		# DateTime for the pin, in UTC
		self.time			= time

		# Title (Main text visible on the timeline
		self.title			= title

		# Description (Visible under more details)
		self.description	= Sanitise( description, 384 )

		# Icon path that corresponds to one defined here: https://developer.getpebble.com/guides/timeline/pin-structure/#pin-icons
		self.icon			= icon

		# The timeline token for the pebble
		self.pebbleToken	= pebbleToken

		self.location 		= location
		self.subtitle 		= subtitle
		self.duration 		= duration
		self.source 		= source

		if headings is None:
			self.headings = []
		else:
			self.headings = headings
			
		if paragraphs is None:
			self.paragraphs = []
		else:
			for index in range( len( paragraphs ) ):
				paragraphs[ index ] = Sanitise( paragraphs[ index ], 384 )
			
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
		
	def DataMatchesExistingPin( self ):
		
		headings = []
		paragraphs = []
		
		for i in xrange( len( self.headings ) ):
			headings.append( CalcHash( self.headings[ i ] ) )
			paragraphs.append( CalcHash( self.paragraphs[ i ] ) )
		
		
		data = \
		{
			'time'			: self.time,
			
			'title'			: CalcHash( self.title ),
			'description'	: CalcHash( self.description ),
			'location'		: CalcHash( self.location ),
			'subtitle'		: CalcHash( self.subtitle ),
			'duration'		: CalcHash( str( self.duration ) ),
			'source'		: CalcHash( self.source ),
			
			'headings'		: headings,
			'paragraphs'	: paragraphs
		}
		
		newPin = storage.CreateTimelinePin( self.id, **data )
		
		oldPin = storage.FindTimelinePin( self.id )
		
		if oldPin is not None and oldPin.IsEqualTo( newPin ):
			#There have been no changes since the last time we were given this pin data
			return True
		
		# Save the new pin data
		newPin.put()
		
		return False

	def Send( self ):
		
		now = datetime.now( common.datetime.UTC )
		timeUntilPin = self.time - now
		
		# Can't have pins more than a year in the future
		if timeUntilPin.days > 364:
			logging.warning( "Ignoring pin with id " + str( self.id ) + " as it's more than a year in the future" )
			return ( codes.bad_request, { "message" : "INVALID_DATE_FUTURE" } )
		
		# Can't have pins more than 2 days in the past
		if timeUntilPin.days < -2:
			logging.warning( "Ignoring pin with id " + str( self.id ) + " as it's more than 2 days in the past" )
			return ( codes.bad_request, { "message" : "INVALID_DATE_PAST" } )
		
		if self.DataMatchesExistingPin():
			logging.info( "Skipping pin with id " + str( self.id ) + " as there have been no changes since the previous time this pin was sent to the server" )
			return ( codes.ok, { "message" : "NO_CHANGE" } )
		
		#Convert the python datetime object into an iso8601-ish format for the pebble api
		pebbleDateFormat = "%Y-%m-%dT%H:%M:%SZ"
		timeInPebbleFormat = self.time.strftime( pebbleDateFormat )
		
		lastUpdated = now.strftime( pebbleDateFormat )
		
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
					'status' : codes.ok,
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
		
		if response[ 0 ] != codes.ok:
			
			if response[ 1 ][ "message" ] == "INVALID_JSON":
				logFunc = logging.error
			else:
				logFunc = logging.warning
			
			logFunc( "Create Pin Failed Response: " + str( response[ 1 ] ) )
			logFunc( "Create Pin Failed Request : " + str( config ) )
		
		return ( response[ 0 ], response[ 1 ] )
	
	@staticmethod
	def Delete( id, pebbleToken ):
		# Construct the request config
		config = \
		{
			'request' :
			{
				'url' : "https://timeline-api.getpebble.com/v1/user/pins/" + id,
				'method' : "DELETE",
				
				'headers' :
				{
					'X-User-Token'	: pebbleToken
				},
			},
			
			'response' :
			{
				'success' :
				{
					'status' : codes.ok,
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
	
		logging.info( "Deleting pin: " + id )
	
		response = net.MakeRequest( config )
		
		if response[ 0 ] != codes.ok:
			logging.error( "Delete Pin Failed Response: " + str( response[ 1 ] ) )
			logging.error( "Delete Pin Failed Request : " + str( config ) )
		
		return ( response[ 0 ], response[ 1 ] )