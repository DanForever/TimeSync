// Copyright 2015 Daniel Neve
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

var UI = require( 'ui' );
var Menu = require( 'menu_resources' );

var watchInfo = null;
var timelineToken = null;
var subscribeMenu = null;
var authRequestCard = null;
var authRequestTimeout = null;
var ignoreAuthCallback = true;
var isLoadingCardVisible = false;
var username = "";
var isChalk = false;

if( Pebble.getActiveWatchInfo )
{
	watchInfo = Pebble.getActiveWatchInfo();
	console.log( "Watch Info: " + JSON.stringify( watchInfo, null, 4 ) );

	if( watchInfo !== null )
	{
		isChalk = watchInfo.platform === "chalk";
	}
	
	if( isChalk )
	{
		console.log( "We've got ourselves a PTR here!" );
	}
	else
	{
		console.log( "Typical Pebble" );
	}
}
else
{
	console.log( "Pebble.getActiveWatchInfo not available" );
}

var main = CreateMenu( Menu.MainMenu );
var loadingCard = CreateCard( Menu.PleaseWait );

function CreateCard( config )
{
	console.log( "CreateCard()" );
	
	if( isChalk )
	{
		console.log( "chalk!" );
	
		config.title = "\n    " + config.title;
		config.fullscreen = true;
		
		if( config.body )
		{
			console.log( "has body" );
		
			var indentTemplate = "               ";
			var indents = [  1, 0, 0, 0, 1, 2 ];
			var maxLength = 24;
		
			var carat = 0;
			var length = config.body.length;
			var newBody = "";
			var line = 0;
		
			while( carat < length )
			{
				var indent = indentTemplate.slice( 0, indents[ line ] );
				var lineLength = maxLength - ( indents[ line ] * 2 );
				section = config.body.slice( carat, carat + lineLength )
				
				var formattedSection = indent + section + "\n";
				newBody = newBody + formattedSection;
				
				console.log( "Body   : " + config.body );
				console.log( "Linelen: " + lineLength );
				console.log( "Carat  : " + carat );
				console.log( "Section: '" + section + "'" );
				console.log( "Format : '" + formattedSection + "'" );
				
				carat += lineLength;
				++line;
			}
		
			config.body = newBody;
		}
	}
	
	return new UI.Card( config );
}

function CreateMenu( config )
{
	if( isChalk )
	{
		config.fullscreen = true;
		for( var index in config.sections )
		{
			config.sections[ index ].title = "   " + config.sections[ index ].title;
		}
	}
	
	return new UI.Menu( config );
}

function ShowLoadingCard()
{
	loadingCard.show();
	isLoadingCardVisible = true;
}

function HideLoadingCard()
{
	loadingCard.hide();
	isLoadingCardVisible = false;
}

function HideAuthRequestCard()
{
	if( authRequestCard !== null )
	{
		authRequestCard.hide();
		authRequestCard = null;
	}
}

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
			
			if( watchInfo !== null )
			{
				var analytics = require( 'analytics' );
				analytics.SendWatchInfo( timelineToken, watchInfo );
			}
			
			main.show();
		},
		
		function( error )
		{
			console.log( 'Error getting timeline token: ' + error );
			
			var noTimelineCard = CreateCard( Menu.Error.NoTimelineToken );
			
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

		var dataDeletedCard = CreateCard( cardData );
		dataDeletedCard.show();
		HideLoadingCard();
	}
	else
	{			
		var errorCard = CreateCard( Menu.Error.Unknown );
		errorCard.show();
		HideLoadingCard();
	}
}

function subscriptionSuccessCallback( libname, data )
{
	var cardConfig =
	{
		title: Menu.Title[ libname ],
		body: "Success"
	};
	
	var card = CreateCard( cardConfig );
	card.show();
	HideLoadingCard();
}

function subscriptionFailureCallback( libname, data )
{
	var cardConfig =
	{
		title: Menu.Title[ libname ],
		style: "small",
		body: "Something went wrong accessing your subscription settings :("
	};
	
	var card = CreateCard( cardConfig );
	card.show();
	HideLoadingCard();
}

function showSubscriptionMenu( libname, data )
{
	var callback = function( e )
	{
		var subscribe = require( 'subscribe' );
		
		if( e.item == Menu.SubscribeMenuItems.Subscribe )
		{
			subscribe.Subscribe( timelineToken, libname, subscriptionSuccessCallback, subscriptionFailureCallback );
			ShowLoadingCard();
			subscribeMenu.hide();
		}
		else if( e.item == Menu.SubscribeMenuItems.Unsubscribe )
		{
			subscribe.Unsubscribe( timelineToken, libname, subscriptionSuccessCallback, subscriptionFailureCallback );
			ShowLoadingCard();
			subscribeMenu.hide();
		}
	};
	
	var menuConfig = Menu.SubscribeMenu;
	
	if( username && username !== "" )
	{
		menuConfig.sections[ 0 ].title = username;
	}
	
	if( data.hasOwnProperty( 'subscribed' ) )
	{
		var activeIndex;
		var inactiveIndex;
		
		if( data.subscribed === "yes" )
		{
			console.log( "Putting the tick on Subscribed -> " + data.subscription );
			activeIndex = 0;
			inactiveIndex = 1;
		}
		else
		{
			console.log( "Putting the tick on Unsubscribed -> " + data.subscription );
			activeIndex = 1;
			inactiveIndex = 0;
		}
		
		menuConfig.sections[ 0 ].items[ activeIndex ].icon = "images/check.png";
		menuConfig.sections[ 0 ].items[ inactiveIndex ].icon = null;
	}
	
	subscribeMenu = CreateMenu( menuConfig );
	subscribeMenu.on( 'select', callback );
	subscribeMenu.on( 'hide', function() { username = null; } );
	subscribeMenu.show();
	HideLoadingCard();
	HideAuthRequestCard();
}

function hasAuthCallback( libname, data )
{
	if( !isLoadingCardVisible )
	{
		ShowLoadingCard();
	}
	
	if( data.hasOwnProperty( 'name' ) )
	{
		console.log( "User Authorised: " + data.name );
	
		username = data.name;
	}
	else
	{
		console.log( "No username returned in response" );
	}
	
	var subscribe = require( 'subscribe' );
	
	console.log( "Getting current subscription info..." );
	subscribe.IsSubscribed( timelineToken, libname, showSubscriptionMenu, subscriptionFailureCallback );
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
		authRequestCard = CreateCard( cardConfig );
		
		authRequestCard.on
		(
			'hide',
			function()
			{
				console.log('Hidden!');
				ignoreAuthCallback = true;

				if( authRequestTimeout !== null )
				{
					console.log( "Clearing authRequestTimeout" );
					clearTimeout( authRequestTimeout );
					authRequestTimeout = null;
					
					// This will also force the card to be removed from the queue
					// So that it won't appear when the user presses the back button
					HideAuthRequestCard();
				}
			}
		);
		
		authRequestCard.show();
		HideLoadingCard();
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
	
	var authErrorCard = CreateCard( errorCardConfig );
	authErrorCard.show();
	HideLoadingCard();
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
			ShowLoadingCard();
		}
		else if( e.item == Menu.TVShowTimeItems.Agenda )
		{
			console.log( "e.item == Menu.TVShowTimeItems.Agenda" );
			ignoreAuthCallback = false;
			auth.Auth( timelineToken, "tvshowtime", hasAuthCallback, awaitingAuthCallback, authErrorCallback );
			ShowLoadingCard();
		}
		else if( e.section == Menu.MainMenuItems.Trakt )
		{
			console.log( "e.section == Menu.MainMenuItems.Trakt" );
			
			var ucCard = CreateCard( Menu.Error.UnderConstruction );
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
				
				ShowLoadingCard();
			}
		}
	}
);

FetchTimelineToken();

