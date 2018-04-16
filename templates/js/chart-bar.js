(function() {
  var margin = { top: 60, left: {{ m_l }}, right: {{ m_r }}, bottom: 40}
  var widthSvg = {{ w }}
  var heightSvg = {{ height }}
  var barsX = 125
  var valueLabelsWidth = 120
  var widthScale = widthSvg - margin.left - margin.right - barsX - valueLabelsWidth
  var heightScale = heightSvg - margin.top - margin.bottom

  var container = d3.select("#chart")

  var mainSvg = container.append("svg")
    .attr("width", widthSvg)
    .attr("height", heightSvg)

  var mainG = mainSvg.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")

  var xPositionScale = d3.scaleLinear()
        .range({{ x_range }})

  var yPositionScale = d3.scaleBand()
        .range([0, heightScale])
        .paddingInner(0.2)

  d3.queue()
    .defer(d3.csv, "{{ csv }}")
    .await(ready)


  function ready(error, datapoints) {
    
    generateTitleLine()    
    generateScales()
    generateLabels()
    generateBars()
    generateValueLabels()
    generateSourceLine()

    function generateTitleLine() {
        var titleLine = mainG.append("g")
                .attr("class", "titleLine")
                .attr("transform", "translate(0,0)")

        titleLine
            .append("text")
            .attr("x", 0)
            .attr("y", 0 - margin.top*0.5)
            .text(" {{ title }}")
    }

    function generateScales() {
      datapoints.sort(function(x, y){
       return d3.descending(+x.{{ x_ax }}, +y.{{ x_ax }});
      })
      var yDomain = datapoints.map(function(d) {
        return d.{{ y_ax }}
      })

      xPositionScale
        .domain({{ x_scale }})
      yPositionScale
        .domain(yDomain)
    }

    function generateLabels() {
        var labelsContainer = mainG.append("g")
                .attr("class", "labelsContainer")
                .attr("transform", "translate(0,0")

        labelsContainer.selectAll(".label")
                .data(datapoints)
                .enter().append("text")
                .attr("class", function(d) {
                    return"label " + "label-" + d.{{ y_ax }}.replace(' ', '-')
                })
                .text(function(d) {
                    return d.{{ y_ax }}
                })
                .attr("x", 0)
                .attr("y", function(d){
                    return yPositionScale(d.{{ y_ax }}) + 0.6 * yPositionScale.bandwidth()
                })
                .attr("dy","0.13em")
    }

    function generateBars() {
      var scatterContainer = mainG.append("g")
            .attr("class", "barsContainer")
            .attr("transform", "translate(0,0)")

      scatterContainer.selectAll(".bar")
        .data(datapoints)
        .enter().append("rect")
        .attr("class", function(d) {
            return "bar " + "bar-" + d.{{ y_ax }}.replace(' ', '-')
        })
        .attr("x", barsX)
        .attr("y", function(d) {
            return yPositionScale(d.{{ y_ax }})
        })
        .attr("width", function(d) {
            return xPositionScale(+d.{{ x_ax }})
        })
        .attr("height", yPositionScale.bandwidth())
    }

    function generateValueLabels() {
        var valuesContainer = mainG.append("g")
                .attr("class", "valuesContainer")
                .attr("transform", "translate(0,0")

        valuesContainer
            .selectAll(".value")
            .data(datapoints)
            .enter().append("text")
            .attr("class", function(d) {
                return"value value-" + d.{{ y_ax }}
            })
            .text(function(d,i) {
                if (i === 0)
                {
                    return d.{{ x_ax }} + "{{ x_label }}"
                }
                else
                {
                    return d.{{ x_ax }}
                }
            })
            .attr("x", function(d) {
                return xPositionScale(+d.{{ x_ax }}) + 132
            })
            .attr("y", function(d) {
                return yPositionScale(d.{{ y_ax }}) + 0.7 * yPositionScale.bandwidth()
            })
            .attr("dy","0.13em")
    }

    function generateSourceLine() {
        var sourceLine = mainG.append("g")
                .attr("class", "sourceLine")
                .attr("transform", "translate(0,0)")

        sourceLine
            .append("text")
            .attr("x", 0)
            .attr("y", heightScale + margin.bottom*0.9)
            .text("Source: {{ source }}")
    }

  }
})();