
// Add segments to a slider
$.fn.addSliderSegments = function( amount, orientation )
{
	return this.each
	(
		function()
		{
			if (orientation == "vertical")
			{
				var output = '', i;
				
				for( i = 1; i <= amount - 2; ++i )
				{
					output += '<div class="ui-slider-segment" style="top:' + 100 / (amount - 1) * i + '%;"></div>';
				};
				$(this).prepend( output );
			}
			else
			{
				var segmentGap = 100 / (amount - 1) + "%", segment = '<div class="ui-slider-segment" style="margin-left: ' + segmentGap + ';"></div>';
				$(this).prepend( segment.repeat( amount - 2 ) );
			}
		}
	);
};

// The slider bar itself
var $slider = $( "#tvst-offset-slider" );

// The input box that displays the value of the slider
var $sliderValue = $( "#tvst-offset-value" );

var $agendaSubscriptionToggle = $( "#subscribe-tvst" );

var $tvstAuthWarning = $( "#tvst-noauth-warning" );

// Some CSS adjustment so that the input box is properly aligned with the bar
$slider.css( "vertical-align", "middle" );

// Set the value of the 
$sliderValue.val( tvstHourOffsetInitialValue );

SetHourOffsetState( tvstIsSubscribedToAgenda );

if ($slider.length > 0)
{
	$slider.slider
	(
		{
			min: -12,
			max: 12,
			value: tvstHourOffsetInitialValue,
			orientation: "horizontal",
			slide: function(event, ui)
			{
				$sliderValue.val( ui.value );
			}
		}
	).addSliderSegments($slider.slider("option").max);
}

function SetHourOffsetState( enabled )
{
	$slider.slider({ disabled: !enabled });
	$sliderValue.prop( 'disabled', !enabled );
	
	if( enabled )
	{
		$slider.children( "a" ).css( "background-color", "" );
	}
	else
	{
		$slider.children( "a" ).css( "background-color", "grey" );
	}
}

$sliderValue.change
(
	function()
	{
		$slider.slider({ value: $sliderValue.val() });
	}
);

if ( $agendaSubscriptionToggle.length )
{
	$agendaSubscriptionToggle.bootstrapSwitch();
	
	if( !hasTVShowTimeAuth )
	{
		$agendaSubscriptionToggle.bootstrapSwitch( 'toggleDisabled' );
	}
}

$agendaSubscriptionToggle.on
(
	'switchChange.bootstrapSwitch',
	function( event, subscribed )
	{
		SetHourOffsetState( subscribed );
	}
);

if( hasTVShowTimeAuth )
{
	$tvstAuthWarning.hide();
}
