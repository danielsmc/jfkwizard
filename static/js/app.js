;

var latest_json;

var fetchJson = function() {
	d3.json("/data", handleJson);
};



var handleJson = function(json) {
	latest_json = json;

	var p = d3.select("#pointers").selectAll(".pointer")
		.data(json);

	p.enter()
		.append("div")
		.attr("class","pointer")
		.text("🚂")
		.style("position","fixed");
		// .style("font-size","5em") // doesn't work of iOS


	p.exit()
		.remove();

	refreshScreen();
}

var refreshHed = function() {
	var hed = "LOL no trains ever";
	for (i in latest_json) {
		var pred = latest_json[i];
		if (pred.pred_time >= (new Date).getTime()/1000) {
			hed = pred.branch;
			break;
		}
	}

	if (hed !== d3.select("h1").text())
		d3.select("h1").text(hed);
}

var refreshPointers = function() {
	var yScale = d3.scale.linear()
					.domain([0,600])
					.range(["0%","100%"]);

	d3.select("#pointers").selectAll(".pointer")
		.style("top",function(d) {var secs = d.pred_time-(new Date).getTime()/1000; return yScale(secs)})
		.style("left",
			function(d) {
				if (d.branch == "Braintree") {
					return "0%"
				} else if (d.branch == "Unknown") {
					return "50%"
				}
			})
		.style("right",
			function(d) {
				if (d.branch == "Ashmont") {
					return "0%"
				}
			})
		.style("-webkit-transform",
			function(d) {
				if (d.branch == "Ashmont") {
					return "rotate(90deg) scaleY(-1)"
				} else {
					return "rotate(90deg)"
				}
			})
};

var refreshScreen = function() {
	refreshHed();
	refreshPointers();
}

setInterval(refreshScreen,100);
setInterval(fetchJson,10*1000);
fetchJson();
