
#System Imports
import datetime
import iso8601

PLATFORM = 'FACEBOOK'
PLATFORM_VERSION = "v2.5"

SUBSCRIBE_HANDSHAKE_TOKEN = "ts_fb_hs_tok"

URL_BASE = 'https://graph.facebook.com/'
URL_SUB_AUTH = 'oauth/device'

def ISO8601ToDateTime( strDt ):
	return iso8601.parse_date( strDt )

def DateTimeToISO8601( dt ):
	outputFormat = "%Y-%m-%dT%H:%M:%S%z"
	return dt.strftime( outputFormat )

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
