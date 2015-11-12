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

var mrFacebookMenuEvents =
{
	title : "Events"
};

var mrFacebookMainMenu =
{
	title : "Facebook",
	items :
	[
		mrFacebookMenuEvents
	]
};

var mrTVShowTimeAgenda =
{
	title : "Agenda"
};

var mrTVShowTimeMainMenu =
{
	title : "TVShow Time",
	items :
	[
		mrTVShowTimeAgenda
	]
};

var mrTraktMainMenu =
{
	title : "Trakt",
	items :
	[
		{
			title : "TV Shows"
		}
	]
};

var mrOptionsMenuDeleteData =
{
	title : "Delete my data",
};

var mrOptionsMainMenu =
{
	title : "Options",
	items :
	[
		mrOptionsMenuDeleteData
	]
};

var mrMainMenu =
{
	sections :
	[
		mrFacebookMainMenu,
		mrTVShowTimeMainMenu,
		//mrTraktMainMenu,
		mrOptionsMainMenu
	]
};

var mrSubscribeMenuItem =
{
	title : "Subscribe"
};

var mrUnsubscribeMenuItem =
{
	title : "Unsubscribe"
};

var mrSubscribeMenu =
{
	sections :
	[
		{
			items :
			[
				mrSubscribeMenuItem,
				mrUnsubscribeMenuItem
			]
		}
	]
};

var mrYesMenuItem =
{
	title : "Yes"
};

var mrNoMenuItem =
{
	title : "No"
};

var mrConfirmMenu =
{
	title : "Are you sure?",
	sections :
	[
		{
			items :
			[
				// No is at the top so that the user can't accidentally trigger it
				mrNoMenuItem,
				mrYesMenuItem
			]
		}
	]
};

var mrErrorNoTimelineToken =
{
	title: 'TimeSync',
	subtitle: 'Error!',
	body: 'Could not retrieve timeline token'
};

var mrErrorNoAuth =
{
	title: 'TimeSync',
	subtitle: 'Error!',
	body: 'There was a problem getting authorisation'
};

var mrErrorUnderConstruction =
{
	title: 'TimeSync',
	subtitle: 'Under Construction'
};

var mrPleaseWait =
{
	title: 'TimeSync',
	subtitle: 'Please Wait...'
};

var mrErrorUnknown =
{
	title: 'TimeSync',
	subtitle: 'Something went wrong :('
};

function mrAuthRequest( url, code )
{
	var ob =
	{
		title: 'TimeSync',
		body: url + "\n" + code
	};
	
	return ob;
}

var wrapper =
{
	MainMenu : mrMainMenu,
	SubscribeMenu : mrSubscribeMenu,
	PleaseWait : mrPleaseWait,
	ConfirmMenu : mrConfirmMenu,
	
	MainMenuItems :
	{
		Facebook : mrFacebookMainMenu,
		TVShowTime : mrTVShowTimeMainMenu,
		Trakt : mrTraktMainMenu,
		Options: mrOptionsMainMenu
	},
	
	FacebookItems :
	{
		Events : mrFacebookMenuEvents
	},
	
	TVShowTimeItems :
	{
		Agenda : mrTVShowTimeAgenda
	},
	
	OptionsItems :
	{
		Delete : mrOptionsMenuDeleteData
	},

	SubscribeMenuItems :
	{
		Subscribe : mrSubscribeMenuItem,
		Unsubscribe : mrUnsubscribeMenuItem
	},
	
	ConfirmMenuItems :
	{
		Yes : mrYesMenuItem,
		No : mrNoMenuItem
	},
	
	Error :
	{
		NoTimelineToken : mrErrorNoTimelineToken,
		NoAuth : mrErrorNoAuth,
		UnderConstruction : mrErrorUnderConstruction,
		Unknown: mrErrorUnknown
	},
	
	GetAuthRequest : mrAuthRequest,
	
	Title :
	{
		"fb" : "Facebook",
		"tvshowtime" : "TVShow Time",
		"trakt" : "Trakt.tv"
	}
};

this.exports = wrapper;