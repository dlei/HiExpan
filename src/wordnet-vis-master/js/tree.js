var margin = {top: 40, right: 200, bottom: 40, left: 200},
    width = 1920 - margin.right - margin.left,
    height = 600 - margin.top - margin.bottom;

// var margin = {top: 40, right: 200, bottom: 40, left: 200},
//     width = 1000 - margin.right - margin.left,
//     height = 400 - margin.top - margin.bottom;

var i = 0,
    duration = 750,
    root;

var tree = d3.layout.tree()
    .size([height, width])
    .separation(function(a, b) { return (a.parent == b.parent ? 1 : 1); });;

var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });

var svg = d3.select(".container").append("svg")
    .attr("width", width + margin.right + margin.left)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("class","drawarea")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

// Add tooltip div
var tooltip = d3.select(".container").append("div")
  .attr("class", "tooltip")
  .style("opacity", 1e-6);

var initialDepth = 1;

function toggleChildren(d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else if (d._children) {
        d.children = d._children;
        d._children = null;
    }
    return d;
}


// var num=2;
var treeName="hiexpan_trees/wiki_init.json"
d3.json(treeName, function(error, flare) {
  root = flare;
  root.x0 = height / 2;
  root.y0 = 0;
  console.log('flare', flare);

  function collapse(d) {
    if (d.children) {
      d._children = d.children;
      d._children.forEach(collapse);
      d.children = null;
    }
  }
  root.children.forEach(collapse);
  update(root);
});

d3.select(self.frameElement).style("height", "800px");


$( "#next" ).click(function() {
  num += 1;
  console.log(num);
  $( "#num" ).html(num);
  d3.json("hiexpan_trees/hiexpan_tree" + num + ".json", function(error, flare) {
    root = flare;
    root.x0 = height / 2;
    root.y0 = 0;
    console.log('flare', flare);
    update(root);
  });
});

$( "#prev" ).click(function() {
  num -= 1;
  console.log(num);
  $( "#num" ).html(num);
  d3.json("hiexpan_trees/hiexpan_tree" + num + ".json", function(error, flare) {
    root = flare;
    root.x0 = height / 2;
    root.y0 = 0;
    console.log('flare', flare);
    update(root);
  });
});


var zoom = function() {
    var scale = d3.event.scale,
        translation = d3.event.translate,
        tbound = -height * scale,
        bbound = height * scale,
        lbound = (-width + margin.right) * scale,
        rbound = (width - margin.left) * scale;
    // limit translation to thresholds
    translation = [
        Math.max(Math.min(translation[0], rbound), lbound),
        Math.max(Math.min(translation[1], bbound), tbound)
    ];
    d3.select(".drawarea")
      .attr("transform", "translate(" + translation + ")" + " scale(" + scale + ")");
}

function update(source) {

  // Compute the new tree layout.
  var nodes = tree.nodes(root).reverse(),
      links = tree.links(nodes);

  // Normalize for fixed-depth.
  nodes.forEach(function(d) { d.y = d.depth * 180; });

  // Update the nodes…
  var node = svg.selectAll("g.node")
      .data(nodes, function(d) { return d.id || (d.id = ++i); });

  // Enter any new nodes at the parent's previous position.
  var nodeEnter = node.enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
      .on("mouseover", function(d) {
            console.log(d);
            if(d["keywords"][0]){
              tooltipHtml = ''
              for(var i=0; i<10 && i<d["keywords"].length; i++){
                tooltipHtml = tooltipHtml + d["keywords"][i] + "<br />"
              }
              tooltipHtml = tooltipHtml + "<hr />" + "US:70% <br />" + "non-US:30% <br />"
              tooltip.html(tooltipHtml)
             .style("left", (d3.event.pageX) + "px")
             .style("top", (d3.event.pageY + 20) + "px")
             .style("opacity",1.0);
            }
            else{
              tooltip.style("opacity",1e-6);
            }
      })
      .on("mousemove",function(d){
          tooltip.style("left", (d3.event.pageX) + "px")
                  .style("top", (d3.event.pageY + 20) + "px");
      })
      .on("mouseout", function() {
          // Remove the info text on mouse out.
          // d3.select(this).select('text.info').remove()
          tooltip.style("opacity", 1e-6);
        });
      ;

  nodeEnter.append("circle")
      .attr("r", 1e-6)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; })
          .style({'fill': '#fff',
        'stroke': 'steelblue',
        'stroke-width': '1.5px'})
      .on("click", click)
      ;

  nodeEnter.append("text")
      .attr("x", function(d) { return d.children || d._children ? -12 : 12; })
      .attr("dy", ".35em")
      .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
      .append("a")
         .attr("xlink:href", function (d) {
           return "/search/" + d.taxonID;
         })
         .attr("target", "_blank")
         .style('font', 'bold')
         .style('font-size', 20)
        //  .style("fill-opacity", 0.3)
        // .style("fill", "lightsteelblue")
        .text(function(d) { return d.name; })
        // .call(wrap, 20);
        // .each(function (d) {
        //     if (d.name!=undefined) {
        //        var lines = wordwrap(d.name, 15)
        //       //  console.log(lines);
        //        for (var i = 0; i < lines.length; i++) {
        //           d3.select(this).append("tspan")
        //               .attr("dy",30)
        //               .attr("x",function(d) {
        //                    return d.children1 || d._children1 ? -15 : 15; })
        //                .text(lines[i])
        //         }
        //      }
        //    });

        // .style("fill-opacity", 1e-6);

  // Transition nodes to their new position.
  var nodeUpdate = node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

  // Define the radius of the circle here
  nodeUpdate.select("circle")
      .attr("r", 10)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; })
      .style({'fill': '#fff',
        'stroke': 'steelblue',
        'stroke-width': '1.5px'});

  nodeUpdate.select("text")
      .style("fill-opacity", 1);

  // Transition exiting nodes to the parent's new position.
  var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
      .remove();

  nodeExit.select("circle")
      .attr("r", 1e-6)
      .style({'fill': '#fff',
        'stroke': 'steelblue',
        'stroke-width': '1.5px'});

  nodeExit.select("text")
      .style("fill-opacity", 1e-6);

  // Update the links…
  var link = svg.selectAll("path.link")
      .data(links, function(d) { return d.target.id; })
      .style({        'fill': 'none',
        'stroke': '#ccc',
        'stroke-width': '1.5px'});

  // Enter any new links at the parent's previous position.
  link.enter().insert("path", "g")
      .attr("class", "link")
      .attr("d", function(d) {
        var o = {x: source.x0, y: source.y0};
        return diagonal({source: o, target: o});
      })
      .style({        'fill': 'none',
        'stroke': '#ccc',
        'stroke-width': '1.5px'});

  // Transition links to their new position.
  link.transition()
      .duration(duration)
      .attr("d", diagonal);

  // Transition exiting nodes to the parent's new position.
  link.exit().transition()
      .duration(duration)
      .attr("d", function(d) {
        var o = {x: source.x, y: source.y};
        return diagonal({source: o, target: o});
      })
      .remove();

  // Stash the old positions for transition.
  nodes.forEach(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });

  d3.select("svg")
    .call(d3.behavior.zoom()
    .scaleExtent([0.5, 5])
    .on("zoom", zoom));
}

// Toggle children on click.
function click(d) {
  if (d.children) {
    d._children = d.children;
    d.children = null;
  } else {
    d.children = d._children;
    d._children = null;
  }
  update(d);
}

function mouseover() {
    div.transition()
    .duration(300)
    .style("opacity", 1);
}

function mousemove(d) {
    div
    .text("Info about " + d.name + ":" + d.info)
    .style("left", (d3.event.pageX ) + "px")
    .style("top", (d3.event.pageY) + "px");
}

function mouseout() {
    div.transition()
    .duration(300)
    .style("opacity", 1e-6);
}

function wordwrap(text, max) {
  var regex = new RegExp(".{0,"+max+"}(?:\\s|_|$)","g");
  var lines = [];
  var line;
  while ((line = regex.exec(text))!="") {lines.push(line);}
  return lines
}

function wordwrap2(text) {
   var lines=text.split("_")
   return lines
}

// from http://bl.ocks.org/mbostock/7555321
function wrap(text, width) {
	text.each(function() {
		var text = d3.select(this),
		words = text.text().split(/\s+/).reverse(),
		word,
		line = [],
		lineNumber = 0,
		lineHeight = 1.2, // ems
        x = text.attr("x"),
		y = text.attr("y"),
        dy = text.attr("dy") ? text.attr("dy") : 0;
		tspan = text.text(null).append("tspan").attr("x", x).attr("y", y).attr("dy", dy + "em");
		while (word = words.pop()) {
			line.push(word);
			tspan.text(line.join(" "));
			if (tspan.node().getComputedTextLength() > width) {
				line.pop();
				tspan.text(line.join(" "));
				line = [word];
				tspan = text.append("tspan").attr("x", x).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
			}
		}
	});
}


d3.select("#generate")
    .on("click", writeDownloadLink);

function writeDownloadLink(){
    //get svg element.
    var svgEl = $("svg")[0];
      svgEl.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    var svgData = svgEl.outerHTML;
    var preface = '<?xml version="1.0" standalone="no"?>\r\n';
    var svgBlob = new Blob([preface, svgData], {type:"image/svg+xml;charset=utf-8"});
    var svgUrl = URL.createObjectURL(svgBlob);
    var downloadLink = document.createElement("a");
    downloadLink.href = svgUrl;
    downloadLink.download = 'test.svg';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
};