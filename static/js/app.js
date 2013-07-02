;

d3.json("/data", function(json) {
	if (json.length == 0) {
		d3.select("h1").text("LOL no trains ever");
		return;
	}

	d3.select("h1")
		.text(json[0].branch);

	var scaleMax = d3.max(json,function(d) {return d.secs});
	scaleMax += 60 - (scaleMax%60);
	console.log(scaleMax);

	var yScale = d3.scale.linear()
					.domain([0,scaleMax])
					.range(["0%","100%"]);

	d3	.select("#pointers")
		.selectAll(".pointer")
		.data(json)
		.enter()
		.append("div")
		.attr("class","pointer")
		.text("🚀")
		.style("position","fixed")
		.style("top",function(d) {return yScale(d.secs)})
		.style("left",
			function(d) {
				if (d.branch == "Ashmont") {
					return "95%";
				} else {
					return "0%"
				}
			})

});