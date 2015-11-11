var defines = require( 'defines' );

var delete_data_config =
{
	"request" :
	{
		url: defines.Domain + "delete/v1/",
		type: 'json',
		method: 'delete',
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
		Data : delete_data_config
	}
};

this.exports = wrapper;
