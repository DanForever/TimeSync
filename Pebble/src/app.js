var UI = require( 'ui' );
var Menu = require( 'menu_resources' );

var timelineToken = null;
var main = new UI.Menu( Menu.MainMenu );
var loadingCard = new UI.Card( Menu.PleaseWait );
var subscribeMenu = new UI.Menu( Menu.SubscribeMenu );
	
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

function FacebookAuthCallback( auth )
{
	if( auth.hasAccess )
	{
		subscribeMenu.title = "Facebook";
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
		if( e.section == Menu.MainMenuItems.Facebook )
		{
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
