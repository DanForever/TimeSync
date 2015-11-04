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

#library imports
import requests

#project imports
import secrets.tvshowtime
import defines

PLATFORM = defines.PLATFORM

AUTH_KEY_REQUEST = \
{
	'request' :
	{
		'url' : "https://api.tvshowtime.com/v1/oauth/device/code",
		'method' : "POST",
		
		# form encoded
		'data' :
		{
			'client_id' : secrets.tvshowtime.CLIENT_ID
		}
	},
	
	'response' :
	{
		'success' :
		{
			'exists' : "device_code",
			'status' : requests.codes.ok,
			'map' :
			{
				'public_key' 	: "user_code",
				'private_key' 	: "device_code",
				'url' 			: "verification_url",
				'expires' 		: "expires_in",
				'interval' 		: "interval"
			}
		},
		
		'failure' :
		{
			'map' :
			{
				'error' : "message"
			}
		}
	}
}

AUTH_KEY_POLL = \
{
	'private_key_entry' : ( [ "request", "data" ], "code" ),
	
	'request' :
	{
		'url' : "https://api.tvshowtime.com/v1/oauth/access_token",
		'method' : "POST",
		
		#form encoded
		'data' :
		{
			'client_id'		: secrets.tvshowtime.CLIENT_ID,
			'client_secret'	: secrets.tvshowtime.APP_SECRET
		}
	},
	
	'response' :
	{
		'success' :
		{
			'exists' : "access_token",
			'status' : requests.codes.ok,
			'map' :
			{
				'access_token' : 'access_token'
			}
		},
		
		'failure' :
		{
			'map' :
			{
				'error' : "message"
			}
		}
	}
}
