var mrFacebookMainMenu =
{
	title : "Facebook",
	items :
	[
		{
			title : "Events",
			subtitle : "Subscribe to facebook events"
		},
		{
			title : "Birthdays",
			subtitle : "Subscribe to your friends birthdays"
		}
	]
};

var mrTraktMainMenu =
{
	title : "Trakt",
	items :
	[
		{
			title : "Test"
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
	},
	
	GetAuthRequest : mrAuthRequest
};

this.exports = wrapper;