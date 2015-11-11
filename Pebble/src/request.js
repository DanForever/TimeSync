function request( timelineToken, config, callback )
{
	console.log( "request()" );
	
	config.request.headers[ "X-User-Token" ] = timelineToken;
	
	var ajax = require('ajax');
	
	var responseCallback = function( data, status_code, request )
	{
		console.log( "http: " + status_code );
		console.log( "data: " + JSON.stringify( data, null, 4 ) );

		var results = {};
		for( var status in config.response )
		{
			console.log( "Status: " + data.status );
			console.log( "Eval status: " + status );
			
			if( data.status == status )
			{
				results.status = status;
				console.log( "config: " + JSON.stringify( data, null, 4 ) );
				
				for( var propertyIndex in config.response[ status ] )
				{
					var property = config.response[ status ][ propertyIndex ];
					
					console.log( "Property: " + property );
					results[ property ] = data[ property ];
				}
			}
		}

		callback( results );
	};
	
	ajax( config.request, responseCallback, responseCallback );
}

var wrapper =
{
	Request : request
};

this.exports = wrapper;