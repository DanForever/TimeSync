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

# Imports from the world of tomorrow
from __future__ import absolute_import

#library imports
import requests

#project imports
import secrets.facebook
import facebook.defines as defines
import auth.keys

PLATFORM = defines.PLATFORM

AUTH_KEY_REQUEST = \
{
	'request' :
	{
		'url' : defines.URL_BASE + defines.URL_SUB_AUTH,
		'method' : "POST",
		
		# form encoded
		'params' :
		{
			'type' : 'device_code',
			'client_id' : secrets.facebook.CLIENT_ID,
			'scope' : 'user_events'
		}
	},
	
	'response' :
	{
		'success' :
		{
			'exists' : "code",
			'status' : requests.codes.ok,
			'map' :
			{
				'public_key' 	: "user_code",
				'private_key' 	: "code",
				'url' 			: "verification_uri",
				'expires' 		: "expires_in",
				'interval' 		: "interval"
			}
		},
		
		'failure' :
		{
			'map' :
			{
				'error' : "error"
			}
		}
	}
}

AUTH_KEY_POLL = \
{
	'resolve' :
	{
		# Add variables to the request
		'request' :
		{
			( ( "params", ), "code" ) : "private_key"
		}
	},
	
	'request' :
	{
		'url' : defines.URL_BASE + defines.URL_SUB_AUTH,
		'method' : "POST",
		
		#form encoded
		'params' :
		{
			'type'		: "device_token",
			'client_id' : secrets.facebook.CLIENT_ID
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
				auth.keys.ACCESS_TOKEN_KEY : "access_token"
			}
		},
		
		'failure' :
		{
			'map' :
			{
				'error' : "error"
			}
		}
	}
}
