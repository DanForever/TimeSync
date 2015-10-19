
var version = "v1";

var domain =  "https://timesync-1061.appspot.com/"
var baseUrl = domain + version + "/facebook/";

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
			
			if( 'name' in data )
			{
				returnData.name = data.name;
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

function fbSubscribeCommon( timelineToken, branch, action, callback )
{
	console.log( "fbSubscribeCommon()" );
	
	var url = baseUrl + branch + "/" + action + "/";
	
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
			
			callback( branch, action, true );
		},
		
		function( data, status, request )
		{
			console.log( "Failure to update subscription :(" );
			console.log( "http: " + status );
			console.log( "data: " + JSON.stringify( data, null, 4 ) );
			
			callback( branch, action, false );
		}
	);
}

function fbSubscribe( timelineToken, branch, callback )
{
	console.log( "fbSubscribe()" );
	
	fbSubscribeCommon( timelineToken, branch, "subscribe", callback );
}

function fbUnsubscribe( timelineToken, branch, callback )
{
	console.log( "fbUnsubscribe()" );
	
	fbSubscribeCommon( timelineToken, branch, "unsubscribe", callback );
}

var wrapper =
{
	GetAuth : fbGetAuth,
	Subscribe : fbSubscribe,
	Unsubscribe : fbUnsubscribe
};

this.exports = wrapper;