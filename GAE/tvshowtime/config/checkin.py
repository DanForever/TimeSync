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

#Project Imports
from .. import defines
import auth.keys

WATCH = \
{
	'resolve' :
	{
		# Add variables to the request
		'request' :
		{
			( ( "params", ), "access_token" ) : auth.keys.ACCESS_TOKEN_KEY,
			( ( "data", ), "episode_id" ) : defines.PEBBLE_PIN_ACT_EP_KEY
		}
	},
	
	'request' :
	{
		'url' : "https://api.tvshowtime.com/v1/checkin",
		'method' : "POST",
		
		'params' : {},
		'data' : {}
	},
	
	'response' :
	{
		'success' :
		{
			'status' : requests.codes.ok,
			'map' : {}
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

UNWATCH = \
{
	'resolve' :
	{
		# Add variables to the request
		'request' :
		{
			( ( "params", ), "access_token" ) : auth.keys.ACCESS_TOKEN_KEY,
			( ( "data", ), "episode_id" ) : defines.PEBBLE_PIN_ACT_EP_KEY
		}
	},
	
	'request' :
	{
		'url' : "https://api.tvshowtime.com/v1/checkout",
		'method' : "POST",
		
		'params' : {},
		'data' : {}
	},
	
	'response' :
	{
		'success' :
		{
			'status' : requests.codes.ok,
			'map' : {}
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