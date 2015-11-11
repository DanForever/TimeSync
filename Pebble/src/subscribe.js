

function common( action, timelineToken, libname, successCallback, failureCallback )
{
	console.log( "Subscribe.common() " + libname );
	var configlib = require( libname );
	console.log( "After" );
	var request = require( 'request' );

	var requestCallback = function( results )
	{
		if( results.status == "success" )
		{
			console.log( "Subscribe: Success" );
			successCallback( libname, results );
		}
		else
		{
			console.log( "Subscribe: Failure" );
			failureCallback( libname, results );
		}
	};
	
	console.log( "subscribe config: " + JSON.stringify( configlib.Config[ action ], null, 4 ) );
	request.Request( timelineToken, configlib.Config[ action ], requestCallback );
}

function subscribe( timelineToken, libname, successCallback, failureCallback )
{
	console.log( "Subscribe.subscribe()" );
	common( "Subscribe", timelineToken, libname, successCallback, failureCallback );
}

function unsubscribe( timelineToken, libname, successCallback, failureCallback )
{
	console.log( "Subscribe.unsubscribe()" );
	common( "Unsubscribe", timelineToken, libname, successCallback, failureCallback );
}

var wrapper =
{
	Subscribe : subscribe,
	Unsubscribe : unsubscribe
};

this.exports = wrapper;
