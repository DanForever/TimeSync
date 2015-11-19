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

#system imports
import datetime

#library imports
import requests

#Project imports
import defines

### Retrieving user data ###
def GetCurrentUserData( accessToken ):
	url = defines.URL_BASE + defines.PLATFORM_VERSION + "/me"
	
	payload = \
	{
		'access_token' : accessToken,
	}
	
	response = requests.get( url, params = payload )
	return ( response.status_code, response.json() )
	
def GetEvents( accessToken ):
	url = defines.URL_BASE + defines.PLATFORM_VERSION + "/me/events"
	
	# Since the timeline can't be populated with anything older than 2 days ago
	# We limit the query to recent and future events
	since = datetime.datetime.now( defines.UTC ) - datetime.timedelta( days = 2 )
	
	nowInFacebookFormat = defines.DateTimeToISO8601( since )
	
	payload = \
	{
		'access_token' : accessToken,
		'since' : nowInFacebookFormat
	}
	
	response = requests.get( url, params = payload )
	return ( response.status_code, response.json() )