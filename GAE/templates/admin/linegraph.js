{% autoescape off %}

var ctx = $( "#{{ id }}" ).get( 0 ).getContext( "2d" );

var data =
{
    labels: [{{ labels }}],
    datasets:[{{ datasets }}]
};

var myLineChart = new Chart( ctx ).Line( data, null );

$( "#{{ id }}_legend" ).append( myLineChart.generateLegend() )

{% endautoescape %}