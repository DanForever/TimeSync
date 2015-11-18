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
import importlib

#Google Imports
import webapp2
from google.appengine.ext.webapp import template

#Library Imports
from requests import codes

class Handler( webapp2.RequestHandler ):
	def get( self, **params ):
		self.exceptionWrapper( params, "get" )
		
	def post( self, **params ):
		self.exceptionWrapper( params, "post" )
	
	def delete( self, **params ):
		self.exceptionWrapper( params, "delete" )
	
	def exceptionWrapper( self, params, method ):
		try:
			self.common( params, method )
		except Exception as e:
			import traceback
			stack = traceback.format_exc()
			logging.error( "Error" )
			logging.error( "Params: " + str( params ) )
			logging.error( "Method: " + str( method ) )
			logging.error( stack )
			self.response.set_status( codes.internal_server_error )
		
	def common( self, params, method ):
		logging.debug( "Base Handler" )
		
		#Fetch config from derived class
		config = self.GetConfig()
		
		logging.debug( "Params: " + str( params ) )
		if "handler" in params:
			branch = None
			handlerConfig = config[ params[ "handler" ] ]
			if method in handlerConfig:
				methodConfig = handlerConfig[ method ]
			
				if "branch" in params and params[ "branch" ] in methodConfig:
					branch = methodConfig[ params[ "branch" ] ]
				elif "default" in methodConfig:
					branch = methodConfig[ "default" ]
			
			if branch is None:
				logging.warning( "Invalid branch" )
				self.response.set_status( codes.not_found )
			
			# Import library
			lib = importlib.import_module( handlerConfig[ "lib" ] )
			
			# Create handler
			handler = lib.Handler( self.app, self.request )
			
			# Call branch
			getattr( handler, branch )( params )
			
			self.response.set_status( handler.response.status )
			self.response.write( handler.response.data )
		else:
			logging.warning( "Invalid handler or method" )
			self.response.set_status( codes.not_found )