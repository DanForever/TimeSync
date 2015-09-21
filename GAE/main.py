#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
import webapp2
import facebook
import requests
import logging
import os
import beta
from google.appengine.ext.webapp import template

class DefaultHandler( webapp2.RequestHandler ):
	def get( self ):
		self.response.write( "Hello" )

class BetaHandler( webapp2.RequestHandler ):
	def get( self ):
		path = "./templates/beta.template"
		values = {}
		self.response.write( template.render( path, values ) )

class CallbackHandler( webapp2.RequestHandler ):
	def common( self, version, handler, func ):
		handlers = \
		{
			"facebook" : facebook
		}
		
		try:
			handler = handlers[ handler ].CallbackHandler( self.app, self.request )
		except:
			# Failed to create the handler object, (aka, a valid one doesn't exist - 404)
			self.response.set_status( requests.codes.not_found )
		
		try:
			getattr( handler, func )()
			
			self.response.set_status( handler.response.status )
			self.response.write( handler.response.data )
			
		except Exception as e:
			import traceback
			stack = traceback.format_exc()
			logging.error( "Unknown Error: " + str( e ) )
			logging.error( stack )
			
			self.response.set_status( requests.codes.internal_server_error )
	
	def get( self, version, handler ):
		self.common( version, handler, "Get" )
		
	def post( self, version, handler ):
		self.common( version, handler, "Post" )

class MainHandler( webapp2.RequestHandler ):
	def post( self, version, handler, branch, action ):
	
		handlers = \
		{
			"facebook" : facebook
		}
		
		try:
			handler = handlers[ handler ].Handler( self.app, self.request )
			handler.Process( branch, action )
			
			self.response.set_status( handler.response.status )
			
			self.response.write( handler.response.data )
			self.response.headers[ "Content-Type" ] = "application/json"
			
		except requests.exceptions.RequestException as e:
			logging.error( "Requests Error: " + str( e ) )
			
		except Exception as e:
			import traceback
			stack = traceback.format_exc()
			logging.error( "Unknown Error: " + str( e ) )
			logging.error( stack )

app = webapp2.WSGIApplication \
(
	[
		webapp2.Route( '/', DefaultHandler ),
		webapp2.Route( '/beta/', BetaHandler ),
		webapp2.Route( '/beta/upload/', beta.FormHandler ),
		webapp2.Route( '/beta/upload/submit/', beta.UploadHandler ),
		webapp2.Route( '/beta/download/', beta.DownloadHandler ),
		webapp2.Route( '/v<version:\d+>/callback/<handler:\w+>/', CallbackHandler, 'callback' ),
		webapp2.Route( '/v<version:\d+>/<handler:\w+>/<branch:\w+>/<action:\w+>/', MainHandler ),
	],
	debug = os.environ[ 'SERVER_SOFTWARE' ].startswith( 'Development' )
)
