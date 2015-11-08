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

# System Imports
import logging

# Library Imports
import requests

def SetDictEntry( dest, config, value ):
	logging.debug( "SetDictEntry() dest " + str( dest ) )
	logging.debug( "SetDictEntry() config " + str( config ) )
	logging.debug( "SetDictEntry() value " + str( value ) )
	
	if( isinstance( config, basestring ) ):
		logging.debug( "Woobly" )
		config = [ config ]
		logging.debug( str( config ) )
	logging.debug( str( config ) )
	path = config[ 0 ]
	
	return reduce( dict.__getitem__, path, dest ).update( { config[ 1 ] : value } )

def FindDictEntry( source, path ):
	return reduce( dict.__getitem__, path, source )

def MapResponse( map, response ):
	out = {}
	for key, value in map.iteritems():
		out[ key ] = response[ value ]
	return out

def Resolve( type, config, db ):
	logging.debug( "Resolve()" )
	try:
		source = config[ "resolve" ][ type ]
		dest = config[ type ]
	except:
		return
	
	logging.debug( "Source: " + str( source ) )
	logging.debug( "Dest before: " + str( dest ) )

	for path in source:
		logging.debug( "Path: " + str( path ) )
		SetDictEntry( dest, path, db[ path[ 1 ] ] )
		
	logging.debug( "Dest after: " + str( dest ) )

def MakeRequest( config, db = None ):
	if db is not None:
		Resolve( "request", config, db )
		Resolve( "response", config, db )
		logging.debug( "After Resolve: " + str( config ) )
	
	response = requests.request( **config[ "request" ] )
	responseObject = response.json()
	
	successConfig = config[ "response" ][ "success" ]
	if response.status_code == successConfig[ "status" ] and successConfig[ "exists" ] in responseObject:
		out = MapResponse( successConfig[ "map" ], responseObject )
		status = requests.codes.ok
	else:
		out = MapResponse( config[ "response" ][ "failure" ][ "map" ], responseObject )
		status = requests.codes.bad_request
	return ( status, out )