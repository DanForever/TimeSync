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

#System Imports
import datetime

# This class is a hack to avoid installing/importing pytz
ZERO = datetime.timedelta( 0 )
class timezoneUTC(datetime.tzinfo):
	"""UTC"""

	def utcoffset( self, dt ):
		return ZERO
	
	def tzname( self, dt ):
		return "UTC"
	
	def dst( self, dt ):
		return ZERO

UTC = timezoneUTC()
