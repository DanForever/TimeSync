var UI = require( 'ui' );
var Menu = require( 'menu_resources' );

var timelineToken = null;
var main = new UI.Menu( Menu.MainMenu );
var loadingCard = new UI.Card( Menu.PleaseWait );
var subscribeMenu = new UI.Menu( Menu.SubscribeMenu );
var facebookBranch = "";

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

function FacebookSubscribeCallback( branch, action, success )
{
	if( success )
	{
		console.log( "FacebookSubscribeCallback() Success!" );
		
		var actionStr = ( action == "subscribe" )? "Subscribed to" : "Unsubscribed from";
		
		var cardData =
		{
			title: 'TimeSync',
			subtitle: actionStr + ' Facebook ' + branch
		};
		
		var subscribedCard = new UI.Card( cardData );
		subscribedCard.show();
		loadingCard.hide();
	}
	else
	{
		console.log( "FacebookSubscribeCallback() Failure!" );
		var errorCard = new UI.Card( Menu.PleaseWait );
		errorCard.show();
		loadingCard.hide();
	}
}

function FacebookSubscribeOn( e )
{
	var fb = require( 'fb' );
	if( e.item == Menu.SubscribeMenuItems.Subscribe )
	{
		fb.Subscribe( timelineToken, facebookBranch, FacebookSubscribeCallback );
		loadingCard.show();
	}
	else if( e.item == Menu.SubscribeMenuItems.Unsubscribe )
	{
		fb.Unsubscribe( timelineToken, facebookBranch, FacebookSubscribeCallback );
		loadingCard.show();
	}
}

function FacebookAuthCallback( auth )
{
	if( auth.hasAccess )
	{
		subscribeMenu.on( 'select', FacebookSubscribeOn );
		subscribeMenu.show();
		loadingCard.hide();
	}
	else if( auth.hasCode )
	{
		var authRequestCard = new UI.Card( Menu.GetAuthRequest( auth.url, auth.code ) );
		authRequestCard.show();
	}
	else
	{
		var authErrorCard = new UI.Card( Menu.Error.NoAuth );
		authErrorCard.show();
	}
	
	loadingCard.hide();
}

main.on
(
	'select',
	function( e )
	{
		console.log( "main.on()" );
		
		if( e.section == Menu.MainMenuItems.Facebook )
		{
			console.log( "e.section == Menu.MainMenuItems.Facebook" );
			
			console.log( e.item );
			
			if( e.item == Menu.FacebookItems.Events )
			{
				console.log( "e.items == Menu.FacebookItems.Events" );
				facebookBranch = "events";
			}
			else if( e.item == Menu.FacebookItems.Birthdays )
			{
				console.log( "e.items == Menu.FacebookItems.Birthdays" );
				facebookBranch = "birthdays";
			}
			
			var fb = require( 'fb' );
			fb.GetAuth( timelineToken, FacebookAuthCallback );
			loadingCard.show();
		}
		else if( e.section == Menu.MainMenuItems.Trakt )
		{
			var ucCard = new UI.Card( Menu.Error.UnderConstruction );
			ucCard.show();
		}
	}
);

FetchTimelineToken( timelineToken );
