var mrFacebookMenuEvents =
{
	title : "Events",
	subtitle : "Subscribe to facebook events"
};

var mrFacebookMenuBirthdays =
{
	title : "Birthdays",
	subtitle : "Subscribe to your friends birthdays"
};

var mrFacebookMainMenu =
{
	title : "Facebook",
	items :
	[
		mrFacebookMenuEvents,
		mrFacebookMenuBirthdays
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
		mrTraktMainMenu,
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
		Trakt : mrTraktMainMenu,
		Options: mrOptionsMainMenu
	},
	
	FacebookItems :
	{
		Events : mrFacebookMenuEvents,
		Birthdays : mrFacebookMenuBirthdays
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
	
	GetAuthRequest : mrAuthRequest
};

this.exports = wrapper;