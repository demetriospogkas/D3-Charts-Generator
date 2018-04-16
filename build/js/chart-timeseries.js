(function() {
  var margin = { top: 60, left: 120, right: 60, bottom: 60}
  var widthSvg = 800
  var heightSvg = 700
  var widthScale = widthSvg - margin.left - margin.right
  var heightScale = heightSvg - margin.top - margin.bottom

  var container = d3.select("#chart")

  var mainSvg = container.append("svg")
    .attr("width", widthSvg)
    .attr("height", heightSvg)

  var mainG = mainSvg.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

  var xPositionScale = d3.scaleTime()
        .range([0, widthScale])

  var yPositionScale = d3.scaleLinear()
        .range([heightScale, 0])

  var parseTime = d3.timeParse("%m/%d/%y")

  var line = d3.line()
        .x(function(d){
            return xPositionScale(d.datetime)
        })
        .y(function(d){
            return yPositionScale(+d.dollars_per_barrel)
        })
        .curve(d3.curveCardinal)

  d3.queue()
    .defer(d3.csv, "../static/data/WTI_Historical_1986-2018_sliced.csv", function(d){
        d.datetime = parseTime(d.date)
        return d
    })
    .await(ready)


  function ready(error, datapoints) {
    
    generateTitleLine()    
    generateScales()
    generateLine()
    generateAxes()
    generateSourceLine()

    function generateTitleLine() {
        var titleLine = mainG.append("g")
                .attr("class", "titleLine")
                .attr("transform", "translate(0,0)")

        titleLine
            .append("text")
            .attr("x", 0 - margin.left*0.6)
            .attr("y", 0 - margin.top*0.5)
            .text(" Cushing, OK WTI Spot Price FOB, 2010-2017")
    }

    function generateScales() {
        xPositionScale
            .domain(d3.extent(datapoints, function(d) { 
                return d.datetime; 
            }))
        yPositionScale
            .domain([0.0, 150.0])
    }

    function generateLine() {
      var lineContainer = mainG.append("g")
            .attr("class", "lineContainer")
            .attr("transform", "translate(0,0)")

      lineContainer.append("path")
            .datum(datapoints)
            .attr("class", "linePath")
            .attr("d", line)
    }

    function generateAxes() {
      var timeFormatX = d3.timeFormat("%b %y")

      datapoints.sort(function(x, y){
       return d3.ascending(+x.dollars_per_barrel, +y.dollars_per_barrel);
      })
      var numFormatY = datapoints[datapoints.length-1].dollars_per_barrel > 999 ? d3.format(".2s") : d3.format(",.1f")

      var xAxis = d3.axisBottom(xPositionScale)
            .tickValues([parseTime("1/1/05"), parseTime("1/1/10"), parseTime("1/1/15")])
            .tickFormat(timeFormatX)
      mainG.append("g")
        .attr("class", "axis x-axis")
        .attr("transform", "translate(0," + heightScale + ")")
        .call(xAxis);

      var yAxis = d3.axisLeft(yPositionScale)
            .tickValues([0.0, 75.0, 150.0])
            .tickFormat(function(d, i) {
              if (
                yAxis.ticks() === null && yAxis.tickValues() === null || 
                yAxis.tickValues() != null && yAxis.tickValues().length > 1 && i === yAxis.tickValues().length - 1 || 
                yAxis.ticks() != null && yAxis.ticks().length > 1 && i === yAxis.ticks().length - 1
                )
              {
                return numFormatY(d) + " $ per barrel"
              }
              else
              {
                return numFormatY(d)
              }
            })
      mainG.append("g")
        .attr("class", "axis y-axis")
        .call(yAxis);
    }

    function generateSourceLine() {
        var sourceLine = mainG.append("g")
                .attr("class", "sourceLine")
                .attr("transform", "translate(0,0)")

        sourceLine
            .append("text")
            .attr("x", 0 - margin.left*0.6)
            .attr("y", heightScale + margin.bottom*0.9)
            .text("Source: U.S. Energy Information Administration")
    }

  }
})();