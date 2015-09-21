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

var mrMainMenu =
{
	sections :
	[
		mrFacebookMainMenu,
		mrTraktMainMenu
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
	
	MainMenuItems :
	{
		Facebook : mrFacebookMainMenu,
		Trakt : mrTraktMainMenu
	},
	
	FacebookItems :
	{
		Events : mrFacebookMenuEvents,
		Birthdays : mrFacebookMenuBirthdays
	},

	SubscribeMenuItems :
	{
		Subscribe : mrSubscribeMenuItem,
		Unsubscribe : mrUnsubscribeMenuItem
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