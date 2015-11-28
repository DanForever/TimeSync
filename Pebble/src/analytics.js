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

var defines = require( 'defines' );

var watch_hardware_config =
{
	"request" :
	{
		url: defines.Domain + "v1/analytics/watch/",
		type: 'json',
		method: 'post',
		headers : {},
	},
	
	"response" :
	{
		"success" :
		[
		],
	}
};

function SendWatchInfo( timelineToken, watchInfo )
{
	var watchJson = JSON.stringify( watchInfo );
	watch_hardware_config.request.data = watchInfo;

	var requests = require( 'request' );
	
	requests.Request
	(
		timelineToken,
		watch_hardware_config,
		function( results )
		{
			console.log( "SendWatchInfo() response: " + JSON.stringify( results, null, 4 ) );
		}
	);
}

var wrapper =
{
	SendWatchInfo : SendWatchInfo
};

this.exports = wrapper;
