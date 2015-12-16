
var $eventsSubscriptionToggle = $( "#subscribe-fbev" );
var $fbevAuthWarning = $( "#fbev-noauth-warning" );

$eventsSubscriptionToggle.bootstrapSwitch();

if( hasFacebookAuth )
{
	$fbevAuthWarning.hide();
	$eventsSubscriptionToggle.bootstrapSwitch( 'state', fbIsSubscribedToEvents );
}
else
{
	$eventsSubscriptionToggle.bootstrapSwitch( 'disabled', true );
}

function GetFBEVValues()
{
	values =
	{
		subscribed : $eventsSubscriptionToggle.is( ':checked' ),
	};
	
	return values;
}

// http://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript?page=1&tab=votes#tab-top
function getParameterByName( name, fallback )
{
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? fallback : decodeURIComponent(results[1].replace(/\+/g, " "));
}

var $saveButton = $( "#save" );

$( document ).ready
(
	function()
	{
		$saveButton.click
		(
			function()
			{
				$saveButton.prop( 'disabled', true );
				$( "#save-indicator" ).show();
				$( "#save-txt" ).hide();
				
				var data =
				{
					tvst : GetTVSTValues(),
					fbev : GetFBEVValues()
				}
				
				$.ajax
				(
					{
						type: "POST",
						url: "/v1/settings/save/" + pebbleToken + "/",
						data: JSON.stringify( data ),
						contentType: "application/json; charset=utf-8",
						dataType: "json",
						complete: function()
						{
							var return_to = getParameterByName( 'return_to', 'pebblejs://close#' );
							document.location = return_to;
						}
					}
				);
			}
		)
	}
);

