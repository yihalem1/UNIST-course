// Set the dimensions and margins of the graph
var margin = {top: 10, right: 30, bottom: 30, left: 60},
    width = 460 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;

// Append the svg object to the body of the page
var svg = d3.select("body")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// Add X axis
var x = d3.scaleLinear()
  .domain([10, 90])
  .range([0, width]);
svg.append("g")
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(x));

// Add Y axis
var y = d3.scaleLinear()
  .domain([0.5, 9])
  .range([ height, 0]);
svg.append("g")
  .call(d3.axisLeft(y));

// Load the data
Promise.all([
  d3.csv("fertility_rate.csv"),
  d3.csv("life_expectancy.csv"),
  d3.csv("population.csv")
]).then(function(files) {
  var fertility = files[0];
  var lifeExpectancy = files[1];
  var population = files[2];

  var data = fertility.map(function(d, i) {
    var country = d["Country Name"];
    
    // If country name is not defined, return null
    if(!country) {
      console.error(`Country name not found at index ${i}`);
      return null;
    }
  
    var fertility = +d["1999"];
    
    if (i >= lifeExpectancy.length || i >= population.length) {
      console.error(`Missing data for ${country} in lifeExpectancy or population`);
      return null;
    }
  
    var lifeExpectancyValue = +lifeExpectancy[i]["1999"];
    var populationValue = +population[i]["1999"];
  
    if (isNaN(fertility) || isNaN(lifeExpectancyValue) || isNaN(populationValue)) {
      console.error(`Invalid data for ${country} in 1999: fertility=${fertility}, lifeExpectancy=${lifeExpectancyValue}, population=${populationValue}`);
      return null;
    } else {
      return {
        country: country,
        fertility: fertility,
        lifeExpectancy: lifeExpectancyValue,
        population: populationValue
      };
    }
  }).filter(d => d !== null);
  
  
  

  // Add dots
  svg.append('g')
    .selectAll("dot")
    .data(data)
    .enter()
    .append("circle")
      .attr("cx", function (d) { return x(d.lifeExpectancy); } )
      .attr("cy", function (d) { return y(d.fertility); } )
      .attr("r", function (d) { 
        var radius = Math.sqrt(d.population / 10000000);
        console.log(radius);
        return radius;
      })
      .style("fill", "#69b3a2")
      .style("opacity", "0.7")
      .attr("stroke", "white");
}).catch(function(err) {
  // handle error here
  console.log(err);
});

  // Set the dimensions and margins of the graph
var margin = {top: 30, right: 30, bottom: 50, left: 60},
width = 460 - margin.left - margin.right,
height = 400 - margin.top - margin.bottom;

var svg = d3.select("body")
.append("svg")
.attr("width", width + margin.left + margin.right)
.attr("height", height + margin.top + margin.bottom)
.append("g")
.attr("transform",
      "translate(" + margin.left + "," + margin.top + ")");

// Add X axis
var x = d3.scaleLinear()
.domain([10, 90])
.range([0, width]);
svg.append("g")
.attr("transform", "translate(0," + height + ")")
.call(d3.axisBottom(x));

// X axis label:
svg.append("text")
.attr("text-anchor", "end")
.attr("x", width/2 + margin.left)
.attr("y", height + margin.top + 20)
.text("Life Expectancy");

// Add Y axis
var y = d3.scaleLinear()
.domain([0.5, 9])
.range([ height, 0]);
svg.append("g")
.call(d3.axisLeft(y));

// Y axis label:
svg.append("text")
.attr("text-anchor", "end")
.attr("transform", "rotate(-90)")
.attr("y", -margin.left+20)
.attr("x", -margin.top-height/2+20)
.text("Fertility Rate")

// Title (Year)
svg.append("text")
.attr("x", (width / 2))             
.attr("y", 0 - (margin.top / 2))
.attr("text-anchor", "middle")  
.style("font-size", "16px") 
.style("text-decoration", "underline")  
.text("Year: 1999");

Promise.all([
d3.csv("fertility_rate.csv"),
d3.csv("life_expectancy.csv"),
d3.csv("population.csv")
]).then(function(files) {
// ...

var colors = d3.scaleOrdinal(d3.schemeCategory10);

// Add dots
svg.append('g')
.selectAll("dot")
.data(data)
.enter()
.append("circle")
  .attr("cx", function (d) { return x(d.lifeExpectancy); } )
  .attr("cy", function (d) { return y(d.fertility); } )
  .attr("r", function (d) { return Math.sqrt(d.population / 10000000); } )
  .style("fill", function(d, i) { return colors(i); }) // Different color for each bubble
  .style("opacity", "0.7")
  .attr("stroke", "white");
}).catch(function(err) {
// handle error here
console.log(err);
});
