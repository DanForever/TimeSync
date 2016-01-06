
Chart.defaults.Line.legendTemplate = 
"<ul style=\"list-style-type:none\" class=\"<%=name.toLowerCase()%>-legend\"> \
	<% for (var i=0; i<datasets.length; i++){%> \
	<li> \
		<span style=\"-moz-border-radius:7px 7px 7px 7px; border-radius:7px 7px 7px 7px; margin-right:10px;width:15px;height:15px;display:inline-block;background-color:<%=datasets[i].fillColor%>\"></span> \
		<%if(datasets[i].label){%> \
			<%=datasets[i].label%> \
		<%}%> \
	</li> \
	<%}%> \
</ul>";


Chart.defaults.Doughnut.legendTemplate = 
"<ul style=\"list-style-type:none\" class=\"<%=name.toLowerCase()%>-legend\"> \
	<% for (var i=0; i<segments.length; i++){%> \
	<li> \
		<span style=\"-moz-border-radius:7px 7px 7px 7px; border-radius:7px 7px 7px 7px; margin-right:10px;width:15px;height:15px;display:inline-block;background-color:<%=segments[i].fillColor%>\"></span> \
		<%if(segments[i].label){%> \
			<%=segments[i].label%> \
		<%}%> \
	</li> \
	<%}%> \
</ul>";