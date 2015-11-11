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
import os
from json import dumps as jsonToString
import importlib

#Google Imports
import webapp2
from google.appengine.ext.webapp import template

#Library Imports
import requests

#Project Imports
import common.storage
import beta
import facebook
import facebook.admin
import facebook.callback
import tvshowtime

class DefaultHandler( webapp2.RequestHandler ):
	def get( self ):
		path = "./templates/index.html"
		values = {}
		self.response.write( template.render( path, values ) )

class AdminHandler( webapp2.RequestHandler ):
	def get( self, **params ):
		self.common( params )
		
	def post( self, **params ):
		self.common( params )
		
	def common( self, params ):
		handlers = \
		{
			"facebook" : facebook.admin
		}
		
		logging.debug( "Admin handler" )
		
		if "handler" in params:
			try:
				logging.debug( "Create admin handler" )
				handler = handlers[ params[ "handler" ] ].Handler( self.app, self.request )
				
				if "branch" in params:
					logging.debug( "Invoke admin branch" )
					getattr( handler, params[ "branch" ].capitalize() )()
				else:
					handler.Main()
					
				self.response.set_status( handler.response.status )
				self.response.write( handler.response.data )
				
			except Exception as e:
				import traceback
				stack = traceback.format_exc()
				logging.error( "Unknown Error: " + str( e ) )
				logging.error( stack )
				
				# Failed to create the handler object, (aka, a valid one doesn't exist - 404)
				self.response.set_status( requests.codes.not_found )
		else:
			self.response.write( template.render( "./templates/admin.html", {} ) )

class BetaHandler( webapp2.RequestHandler ):
	def get( self ):
		path = "./templates/beta.template"
		values = {}
		self.response.write( template.render( path, values ) )

class CallbackHandler( webapp2.RequestHandler ):
	def common( self, version, handler, func ):
		handlers = \
		{
			"facebook" : facebook.callback
		}
		
		try:
			handler = handlers[ handler ].Handler( self.app, self.request )
		
		except Exception as e:
			import traceback
			stack = traceback.format_exc()
			logging.error( "Unknown Error: " + str( e ) )
			logging.error( stack )
			
			# Failed to create the handler object, (aka, a valid one doesn't exist - 404)
			self.response.set_status( requests.codes.not_found )
			logging.error( "Could not find specified handler: '" + handler + "'" )
			return
		
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
			"facebook" : facebook,
			"trakt" : trakt,
			"tvshowtime" : tvshowtime
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
			self.response.set_status( requests.codes.internal_server_error )

class DeleteHandler( webapp2.RequestHandler ):
	def delete( self, version ):
		if 'X-User-Token' not in self.request.headers:
			self.response.set_status( requests.codes.unauthorized )
			return
		
		common.storage.DeleteAllPinsForUser( self.request.headers[ 'X-User-Token' ] )
		
		self.response.set_status( requests.codes.ok )
		response = \
		{
			'status' : "success",
		}
		self.response.write( jsonToString( response ) )

class CronHandler( webapp2.RequestHandler ):
	def get( self, **params ):
		
		handlers = \
		{
			"tvshowtime" : "tvshowtime.cron"
		}
		
		if params[ "handler" ] in handlers:
			lib = handlers[ params[ "handler" ] ]
			logging.debug( "CronHandler() About to import " + lib )
			try:
				cron = importlib.import_module( lib )
				handler = cron.Handler( self.app, self.request )
				handler.Process()
			except Exception as e:
				import traceback
				stack = traceback.format_exc()
				logging.error( "Error during Cron: " + str( e ) )
				logging.error( stack )
				self.response.set_status( requests.codes.internal_server_error )

app = webapp2.WSGIApplication \
(
	[
		webapp2.Route( '/', DefaultHandler ),
		webapp2.Route( '/beta/', BetaHandler ),
		webapp2.Route( '/beta/upload/', beta.FormHandler ),
		webapp2.Route( '/beta/upload/submit/', beta.UploadHandler ),
		webapp2.Route( '/beta/download/', beta.DownloadHandler ),
		webapp2.Route( '/cron/<handler:\w+>/', CronHandler ),
		webapp2.Route( '/v<version:\d+>/callback/<handler:\w+>/', CallbackHandler, 'callback' ),
		webapp2.Route( '/v<version:\d+>/<handler:\w+>/<branch:\w+>/<action:\w+>/', MainHandler, 'mainhandler' ),
		webapp2.Route( '/delete/v<version:\d+>/', DeleteHandler ),
		webapp2.Route( '/admin/', AdminHandler ),
		webapp2.Route( '/admin/<handler:\w+>/', AdminHandler, 'admin_handler' ),
		webapp2.Route( '/admin/<handler:\w+>/<branch:\w+>/', AdminHandler, 'admin_branch' )
	],
	debug = os.environ[ 'SERVER_SOFTWARE' ].startswith( 'Development' )
)
