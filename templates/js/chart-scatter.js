(function() {
  var margin = { top: 60, left: {{ m_l }}, right: {{ m_r }}, bottom: 60}
  var widthSvg = {{ w }}
  var heightSvg = 700
  var widthScale = widthSvg - margin.left - margin.right
  var heightScale = heightSvg - margin.top - margin.bottom

  var container = d3.select("#chart")

  var mainSvg = container.append("svg")
    .attr("width", widthSvg)
    .attr("height", heightSvg)

  var mainG = mainSvg.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

  var xPositionScale = d3.scaleLinear()
        .range([0, widthScale])

  var yPositionScale = d3.scaleLinear()
        .range([heightScale, 0])

  var radiusScale = d3.scaleSqrt()
        .range({{ r_range }})

  d3.queue()
    .defer(d3.csv, "{{ csv }}")
    .await(ready)


  function ready(error, datapoints) {
    
    generateTitleLine()    
    generateScales()
    generateScatter()
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
            .text(" {{ title }}")
    }

    function generateScales() {
      xPositionScale
        .domain({{ x_scale }})
      yPositionScale
        .domain({{ y_scale }})
      radiusScale
        .domain({{ r_dom }})
    }

    function generateScatter() {
      var scatterContainer = mainG.append("g")
            .attr("class", "scatterContainer")
            .attr("transform", "translate(0,0)")

      scatterContainer.selectAll(".scatterCircles")
        .data(datapoints)
        .enter().append("circle")
        .attr("class", "scatterCircles")
        .attr("cx", function(d) {
          return xPositionScale(+d.{{ x_ax }})
        })
        .attr("cy", function(d) {
          return yPositionScale(+d.{{ y_ax }})
        })
        .attr("r", function(d){
            return {{ r_attr }}
        })
    }

    function generateAxes() {
      datapoints.sort(function(x, y){
       return d3.ascending(+x.{{ x_ax }}, +y.{{ x_ax }});
      })
      var numFormatX = datapoints[datapoints.length-1].{{ x_ax }} > 999 ? d3.format(".2s") : d3.format(",.1f")
      
      datapoints.sort(function(x, y){
       return d3.ascending(+x.{{ y_ax }}, +y.{{ y_ax }});
      })
      var numFormatY = datapoints[datapoints.length-1].{{ y_ax }} > 999 ? d3.format(".2s") : d3.format(",.1f")

      var xAxis = d3.axisBottom(xPositionScale)
            {{ x_ticks }}
            .tickFormat(function(d, i) {
              if (
                xAxis.ticks() === null && xAxis.tickValues() === null || 
                xAxis.tickValues() != null && xAxis.tickValues().length > 1 && i === xAxis.tickValues().length - 1 || 
                xAxis.ticks() != null && xAxis.ticks().length > 1 && i === xAxis.ticks().length - 1
                )
              {
                return numFormatX(d) + "{{ x_label }}"
              }
              else
              {
                return numFormatX(d)
              }
            })
      mainG.append("g")
        .attr("class", "axis x-axis")
        .attr("transform", "translate(0," + heightScale + ")")
        .call(xAxis);

      var yAxis = d3.axisLeft(yPositionScale)
            {{ y_ticks }}
            .tickFormat(function(d, i) {
              if (
                yAxis.ticks() === null && yAxis.tickValues() === null || 
                yAxis.tickValues() != null && yAxis.tickValues().length > 1 && i === yAxis.tickValues().length - 1 || 
                yAxis.ticks() != null && yAxis.ticks().length > 1 && i === yAxis.ticks().length - 1
                )
              {
                return numFormatY(d) + "{{ y_label }}"
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
            .text("Source: {{ source }}")
    }

  }
})();