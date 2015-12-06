
var $eventsSubscriptionToggle = $( "#subscribe-fbev" );
var $fbevAuthWarning = $( "#fbev-noauth-warning" );

$eventsSubscriptionToggle.bootstrapSwitch();

if( hasFacebookAuth )
{
	$fbevAuthWarning.hide();
}
else
{
	$eventsSubscriptionToggle.bootstrapSwitch( 'disabled', true );
}