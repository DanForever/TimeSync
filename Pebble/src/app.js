var UI = require( 'ui' );
var Menu = require( 'menu_resources' );

var timelineToken = null;
var main = new UI.Menu( Menu.MainMenu );
var loadingCard = new UI.Card( Menu.PleaseWait );
var subscribeMenu = new UI.Menu( Menu.SubscribeMenu );
var authRequestCard = null;
var authRequestTimeout = null;
var ignoreAuthCallback = true;

function FetchTimelineToken()
{
	console.log( "Fetching timeline token" );
	if( timelineToken !== null )
	{
		console.log( "Timeline token already present" );
		
		return false;
	}
	
	Pebble.getTimelineToken
	(
		function( token )
		{
			timelineToken = token;
			console.log( 'Timeline token successfully retrieved: ' + token );
			
			main.show();
		},
		
		function( error )
		{
			console.log( 'Error getting timeline token: ' + error );
			
			var noTimelineCard = new UI.Card( Menu.Error.NoTimelineToken );
			
			noTimelineCard.show();
		}
	);
	
	return true;
}

function deleteMyDataCallback( results )
{
	if( results.status == "success" )
	{
		var cardData =
		{
			title: 'TimeSync',
			subtitle: "Data deleted!"
		};

		var dataDeletedCard = new UI.Card( cardData );
		dataDeletedCard.show();
		loadingCard.hide();
	}
	else
	{			
		var errorCard = new UI.Card( Menu.Error.Unknown );
		errorCard.show();
		loadingCard.hide();
	}
}

function subscriptionSuccessCallback( libname, data )
{
	var cardConfig =
	{
		title: Menu.Title[ libname ],
		style: "small",
		body: "Success"
	};
	
	var card = new UI.Card( cardConfig );
	card.show();
	loadingCard.hide();
}

function subscriptionFailureCallback( libname, data )
{
	var cardConfig =
	{
		title: Menu.Title[ libname ],
		style: "small",
		body: "Something went wrong configuring your subscription settings :("
	};
	
	var card = new UI.Card( cardConfig );
	card.show();
	loadingCard.hide();
}

function hasAuthCallback( libname, data )
{
	var callback = function( e )
	{
		var subscribe = require( 'subscribe' );
		
		if( e.item == Menu.SubscribeMenuItems.Subscribe )
		{
			subscribe.Subscribe( timelineToken, libname, subscriptionSuccessCallback, subscriptionFailureCallback );
			loadingCard.show();
		}
		else if( e.item == Menu.SubscribeMenuItems.Unsubscribe )
		{
			subscribe.Unsubscribe( timelineToken, libname, subscriptionSuccessCallback, subscriptionFailureCallback );
			loadingCard.show();
		}
	};
	
	console.log( "User Authorised: " + data.name );
	
	subscribeMenu.on( 'select', callback );
	subscribeMenu.show();
	loadingCard.hide();
	if( authRequestCard !== null )
	{
		authRequestCard.hide();
		authRequestCard = null;
	}
}

function awaitingAuthCallback( libname, data )
{
	if( ignoreAuthCallback )
	{
		return;
	}
	
	var cardConfig =
	{
		title: Menu.Title[ libname ],
		style: "mono",
		body: data.url + "\n" + data.code
	};
	
	if( authRequestCard === null )
	{
		authRequestCard = new UI.Card( cardConfig );
		
		authRequestCard.on
		(
			'hide',
			function()
			{
				console.log('Hidden!');
				ignoreAuthCallback = true;

				if( authRequestTimeout !== null )
				{
					clearTimeout( authRequestTimeout );
					authRequestTimeout = null;
				}
			}
		);
		
		authRequestCard.show();
		loadingCard.hide();
	}
	
	authRequestTimeout = setTimeout
	(
		function()
		{
			var auth = require( 'auth' );
			auth.Auth( timelineToken, libname, hasAuthCallback, awaitingAuthCallback, authErrorCallback );
		},
		data.interval * 1000
	);
}

function authErrorCallback( libname, data )
{
	var errorCardConfig =
	{
		title: Menu.Title[ libname ],
		subtitle: 'Something went wrong :(',
		body: 'There was a problem getting authorisation'
	};
	
	var authErrorCard = new UI.Card( errorCardConfig );
	authErrorCard.show();
	loadingCard.hide();
}

main.on
(
	'select',
	function( e )
	{
		console.log( "main.on()" );
		var auth = require( 'auth' );
		
		if( e.item == Menu.FacebookItems.Events )
		{
			console.log( "e.items == Menu.FacebookItems.Events" );
			ignoreAuthCallback = false;
			auth.Auth( timelineToken, "fb", hasAuthCallback, awaitingAuthCallback, authErrorCallback );
			loadingCard.show();
		}
		else if( e.item == Menu.TVShowTimeItems.Agenda )
		{
			console.log( "e.item == Menu.TVShowTimeItems.Agenda" );
			ignoreAuthCallback = false;
			auth.Auth( timelineToken, "tvshowtime", hasAuthCallback, awaitingAuthCallback, authErrorCallback );
		}
		else if( e.section == Menu.MainMenuItems.Trakt )
		{
			console.log( "e.section == Menu.MainMenuItems.Trakt" );
			
			var ucCard = new UI.Card( Menu.Error.UnderConstruction );
			ucCard.show();
		}
		else if( e.section == Menu.MainMenuItems.Options )
		{
			console.log( "e.section == Menu.MainMenuItems.Options" );
			
			if( e.item == Menu.OptionsItems.Delete )
			{
				console.log( "e.item == Menu.OptionsItems.Delete" );
				
				var request = require( 'request' );
				var deleteme = require( 'deleteme' );
				
				request.Request( timelineToken, deleteme.Config.Data, deleteMyDataCallback );
				
				loadingCard.show();
			}
		}
	}
);

FetchTimelineToken();
