
var ctx = $( "#{{ id }}" ).get( 0 ).getContext( "2d" );

var data =
[
	{% for section in sections %}
	{
		value: {{ section.value }},
		color: "{{ section.colour }}",
		highlight: "{{ section.highlight }}",
		label: "{{ section.name }}"
	},
	{% endfor %}
];

var myDoughnutChart = new Chart( ctx ).Doughnut( data, null );
