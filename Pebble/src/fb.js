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

var defines = require( 'defines' );

var auth_config =
{
	"request" :
	{
		url: defines.Domain + "v1/facebook/auth/request/",
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
		url: defines.Domain + "v1/facebook/events/subscribe/",
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
		url: defines.Domain + "v1/facebook/events/unsubscribe/",
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

var check_subscription_config =
{
	"request" :
	{
		url: defines.Domain + "v1/facebook/events/issubscribed/",
		type: 'json',
		method: 'post',
		headers : {},
	},
	
	"response" :
	{
		"success" :
		[
			"subscribed"
		],
		"require_auth" : [],
	}
};

var wrapper =
{
	Config :
	{
		Auth : auth_config,
		Subscribe : subscribe_config,
		Unsubscribe : unsubscribe_config,
		IsSubscribed : check_subscription_config
	}
};

this.exports = wrapper;
