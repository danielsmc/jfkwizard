;

var latest_json = [];

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
		.style("position","fixed");
		// .style("font-size","5em") // doesn't work of iOS


	p.exit()
		.remove();

	refreshScreen();
}

var refreshHed = function() {
	var hed = "LOL nope";
	var caveat = "";
	for (var i = 0; i<latest_json.length; i++) {
		var pred = latest_json[i];
		if (pred.pred_time >= (new Date).getTime()/1000) {
			hed = pred.branch;
			if (((latest_json.length-1) > i) && (latest_json[i+1].pred_time - pred.pred_time) < 30) {
				caveat = "It's going to be close, though.";
			}
			break;
		}
	}

	if (hed !== d3.select("#platform").text())
		d3.select("#platform").text(hed);

	if (caveat !== d3.select("#caveat").text())
		d3.select("#caveat").text(caveat);
}

var refreshPointers = function() {
	var yScale = d3.scale.linear()
					.domain([0,600])
					.range(["0%","100%"]);

	d3.select("#pointers").selectAll(".pointer")
		.text(
			function(d) {
				var train = "🚂";
				if (d.branch == "Braintree") {
					return train+"B";
				} else if (d.branch == "Ashmont") {
					return train+"A";
				} else {
					return train;
				}
			})
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

if (window.navigator.standalone === false) {
	d3.select("#install-hint").style("display","block");
}

setInterval(refreshScreen,100);
setInterval(fetchJson,10*1000);
fetchJson();
