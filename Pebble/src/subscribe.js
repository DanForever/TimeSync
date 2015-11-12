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

function common( action, timelineToken, libname, successCallback, failureCallback )
{
	console.log( "Subscribe.common() " + libname );
	var configlib = require( libname );
	console.log( "After" );
	var request = require( 'request' );

	var requestCallback = function( results )
	{
		if( results.status == "success" )
		{
			console.log( "Subscribe: Success" );
			successCallback( libname, results );
		}
		else
		{
			console.log( "Subscribe: Failure" );
			failureCallback( libname, results );
		}
	};
	
	console.log( "subscribe config: " + JSON.stringify( configlib.Config[ action ], null, 4 ) );
	request.Request( timelineToken, configlib.Config[ action ], requestCallback );
}

function subscribe( timelineToken, libname, successCallback, failureCallback )
{
	console.log( "Subscribe.subscribe()" );
	common( "Subscribe", timelineToken, libname, successCallback, failureCallback );
}

function unsubscribe( timelineToken, libname, successCallback, failureCallback )
{
	console.log( "Subscribe.unsubscribe()" );
	common( "Unsubscribe", timelineToken, libname, successCallback, failureCallback );
}

function isSubscribed( timelineToken, libname, successCallback, failureCallback )
{
	console.log( "Subscribe.isSubscribed()" );
	common( "IsSubscribed", timelineToken, libname, successCallback, failureCallback );
}

var wrapper =
{
	Subscribe : subscribe,
	Unsubscribe : unsubscribe,
	IsSubscribed : isSubscribed
};

this.exports = wrapper;
