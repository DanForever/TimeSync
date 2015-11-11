var defines = require( 'defines' );

var auth_config =
{
	"request" :
	{
		url: defines.Domain + "v1/tvshowtime/auth/request/",
		type: 'json',
		method: 'post',
		headers : {},
	},
	
	"response" :
	{
		"success" :
		[
			"name"
		],
		
		"require_auth" :
		[
			"code",
			"url",
			"interval"
		]
	}
};

var subscribe_config =
{
	"request" :
	{
		url: defines.Domain + "v1/tvshowtime/subscribe/subscribe/",
		type: 'json',
		method: 'post',
		headers : {},
	},
	
	"response" :
	{
		"success" : [],
		"require_auth" : [],
	}
};

var unsubscribe_config =
{
	"request" :
	{
		url: defines.Domain + "v1/tvshowtime/subscribe/unsubscribe/",
		type: 'json',
		method: 'post',
		headers : {},
	},
	
	"response" :
	{
		"success" : [],
		"require_auth" : [],
	}
};

var wrapper =
{
	Config :
	{
		Auth : auth_config,
		Subscribe : subscribe_config,
		Unsubscribe : unsubscribe_config
	}
};

this.exports = wrapper;