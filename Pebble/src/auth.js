


function auth( timelineToken, libname, hasAuthCallback, awaitingAuthCallback, errorCallback )
{
	var configlib = require( libname );
	
	var request = require( 'request' );

	var requestCallback = function( results )
	{
		console.log( "Auth results: " + results + " - " + JSON.stringify( results, null, 4 )  );

		if( results.status == "require_auth" )
		{
			awaitingAuthCallback( libname, results );
		}
		else if( results.status == "success" )
		{
			hasAuthCallback( libname, results );
		}
		else
		{
			errorCallback( libname, errorCallback );
		}
	};
	
	request.Request( timelineToken, configlib.Config.Auth, requestCallback );
}

var wrapper =
{
	Auth : auth
};

this.exports = wrapper;
