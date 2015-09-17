
var version = "v1";
var baseUrl = "https://timesync-1061.appspot.com/" + version + "/facebook/";

function fbGetAuth( timelineToken, callback )
{
	console.log( "fbGetAuth()" );
	
	var url = baseUrl + "auth/request/";
	
	var headers =
	{
		"X-User-Token" : timelineToken,
	};
		
	var ajax = require('ajax');
	
	ajax
	(
		{
			url: url,
			type: 'json',
			method: 'post',
			headers : headers,
		},
		
		function( data, status, request )
		{
			console.log( "SUCCESS! :D" );
			console.log( "http: " + status );
			console.log( "data: " + JSON.stringify( data, null, 4 ) );
			
			var returnData =
			{
				hasCode : data.status == "require_auth",
				hasAccess : data.status == "success"
			};
			
			if( 'code' in data )
			{
				returnData.code	= data.code;
				returnData.url	= data.url;
			}
			
			callback( returnData );
		},
		
		function( data, status, request )
		{
			console.log( "Failure to get auth :(" );
			console.log( "http: " + status );
			console.log( "data: " + JSON.stringify( data, null, 4 ) );
			
			var returnData =
			{
				hasCode : false,
				hasAccess : false
			};
			
			callback( returnData );
		}
	);
}

var wrapper =
{
	GetAuth : fbGetAuth,
};

this.exports = wrapper;