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
from requests import codes

#project imports
import facebook.defines as defines
import auth.keys

EVENTS = \
{
	'resolve' :
	{
		# Add variables to the request
		'request' :
		{
			( ( "params", ), "access_token" ) : auth.keys.ACCESS_TOKEN_KEY,
			( ( "params", ), "since" ) : defines.START_DATE_KEY,
		}
	},
	
	'request' :
	{
		'url' : defines.URL_BASE + defines.PLATFORM_VERSION + "/me/events",
		'method' : "GET",
		
		# form encoded
		'params' : {}
	},
	
	'response' :
	{
		'success' :
		{
			'status' : codes.ok,
			'map' :
			{
				'events' : "data"
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
