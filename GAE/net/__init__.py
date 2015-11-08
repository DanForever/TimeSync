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
	if( isinstance( config, basestring ) ):
		config = [ config ]
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
	try:
		source = config[ "resolve" ][ type ]
		dest = config[ type ]
	except:
		return
	
	for path in source:
		dbKey = source[ path ]
		value = db[ dbKey ]
		
		SetDictEntry( dest, path, value )

def MakeRequest( config, db = None ):
	if db is not None:
		Resolve( "request", config, db )
		Resolve( "response", config, db )
		
	response = requests.request( **config[ "request" ] )
	try:
		responseObject = response.json()
	except:
		responseObject = None
	
	successConfig = config[ "response" ][ "success" ]
	if response.status_code == successConfig[ "status" ] and ( "exists" not in successConfig or successConfig[ "exists" ] in responseObject ):
		out = MapResponse( successConfig[ "map" ], responseObject )
		status = requests.codes.ok
	else:
		out = MapResponse( config[ "response" ][ "failure" ][ "map" ], responseObject )
		status = requests.codes.bad_request
	return ( status, out )