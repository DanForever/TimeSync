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
import iso8601

PLATFORM = 'FACEBOOK'
PLATFORM_VERSION = "v2.5"

SUBSCRIBE_HANDSHAKE_TOKEN = "ts_fb_hs_tok"

URL_BASE = 'https://graph.facebook.com/'
URL_SUB_AUTH = 'oauth/device'

START_DATE_KEY = "from_date"

def ISO8601ToDateTime( strDt ):
	return iso8601.parse_date( strDt )

def DateTimeToISO8601( dt ):
	outputFormat = "%Y-%m-%dT%H:%M:%S%z"
	return dt.strftime( outputFormat )
