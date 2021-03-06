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
import os

#Google Imports
import webapp2

#Project Imports
import base

class AnalyticsHandler( base.Handler ):
	def GetConfig( self ):
		return \
		{
			"analytics" :
			{
				"lib" : "analytics",
				
				"post" :
				{
					"watch" :
					{
						"func" : "WatchInfo",
						
						"out" :
						{
							"headers" :
							{
								"Content-Type" : "application/json"
							}
						}
					}
				}
			}
		}

app = webapp2.WSGIApplication \
(
	[
		webapp2.Route( '/v<version:\d+>/<handler:\w+>/<branch:\w+>/', AnalyticsHandler ),
	],
	debug = os.environ[ 'SERVER_SOFTWARE' ].startswith( 'Development' )
)
