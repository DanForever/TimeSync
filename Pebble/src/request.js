// Copyright 2015 Daniel Neve
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

function request( timelineToken, config, callback )
{
	console.log( "request()" );
	
	config.request.headers[ "X-User-Token" ] = timelineToken;
	
	var ajax = require('ajax');
	
	var responseCallback = function( data, status_code, request )
	{
		console.log( "http: " + status_code );
		console.log( "data: " + JSON.stringify( data, null, 4 ) );

		var results = {};
		for( var status in config.response )
		{
			if( data.status == status )
			{
				results.status = status;
				
				for( var propertyIndex in config.response[ status ] )
				{
					var property = config.response[ status ][ propertyIndex ];
					
					console.log( "Property: " + property );
					results[ property ] = data[ property ];
				}
			}
		}

		callback( results );
	};
	
	ajax( config.request, responseCallback, responseCallback );
}

var wrapper =
{
	Request : request
};

this.exports = wrapper;
