
// Declare global variables for SVG and scales
let svg, xScale, yScale, cScale;
let margin = {top: 5, right: 30, bottom: 50, left: 100},
width = 800 - margin.left - margin.right,
height = 600 - margin.top - margin.bottom;

let selectedCountries = [];

d3.csv('owid-covid-data.csv')
.then(data => {

    // Additional data processing
    data.forEach(function(el){
        el["percent_fully"] = el["people_fully_vaccinated"] / el["population"];
        el["total_percent"] = el["people_vaccinated"] / el["population"];
        el["percent_partly"] = el["total_percent"] - el["percent_fully"];
    })

        // Additional data processing
    data.forEach(function(el){
        el["date"] = d3.timeParse("%Y-%m-%d")(el["date"]);
        el["total_cases"] = +el["total_cases"];
        //...
    });


    const share = data.filter(el => el.people_vaccinated && el.people_fully_vaccinated)

    const getRecent = arr => {
        const res = [], map = {};
    
        arr.forEach(el => {
            if (!(el['location'] in map)) {
               map[el['location']] = res.push(el) - 1;
               return;
            };
            if(res[map[el['location']]]['date'] < el['date']){
               res[map[el['location']]] = el;
            };
        });
        return res;
     };

    const vaccinated = getRecent(share);
    vaccinated.sort(function(a, b){
        return b["total_percent"] - a["total_percent"]
    })

    // Initialize the chart 
    initializeChart(vaccinated, "bar");

    // Add checkboxes for each unique country in the data
    let uniqueCountries = [...new Set(vaccinated.map(d => d.location))];
    let checkboxesDiv = d3.select("#checkboxes");
    uniqueCountries.forEach(country => {
        let checkbox = checkboxesDiv.append('label').text(country).append('input')
            .attr('type', 'checkbox')
            .attr('value', country);
        checkbox.on('change', () => {
            if (checkbox.property('checked')) {
                selectedCountries.push(country);
            } else {
                selectedCountries = selectedCountries.filter(c => c !== country);
            }
            updateChart(filterCountries(vaccinated));
        });
    });

})
.catch(error => {
    console.error('Error loading the data');
});

// Filter data based on selected countries
function filterCountries(data) {
    return data.filter(d => selectedCountries.includes(d.location));
}

// Function to initialize the chart
function initializeChart(data, chartType) {

    svg = d3.select("#chart")
        .append("svg")
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);


        if(chartType === "bar") {
            xScale = d3.scaleLinear()
                .range([0, width])
                .nice();
    
            yScale = d3.scaleBand()
                .range([0, height])
                .padding(0.2);
        } else if(chartType === "line") {
            xScale = d3.scaleTime()
                .range([0, width])
                .domain(d3.extent(data, d => d.date));
    
            yScale = d3.scaleLinear()
                .range([height, 0])
                .domain([0, d3.max(data, d => d.total_cases)]);
        }    

    xScale = d3.scaleLinear()
        .range([0, width])
        .nice();

    yScale = d3.scaleBand()
        .range([0, height])
        .padding(0.2);

    cScale = d3.scaleOrdinal()
        .range(['#7bccc4','#2b8cbe'])
        .domain(["percent_fully", "percent_partly"]);
}

d3.selectAll("input[name='chartType']")
    .on('change', function() {
        let chartType = this.value;
        updateChart(filterCountries(vaccinated), chartType);
    });

// Function to update the chart
function updateChart(data) {


    if (!svg) return; // if the SVG hasn't been created yet, exit


    // Update scales
    xScale.domain([0, d3.max(data, d=>d.total_percent)]);
    yScale.domain(data.map(d => d.location));

    // Define the position of each axis
    const xAxis = d3.axisBottom(xScale).tickFormat(d=>d*100);
    const yAxis = d3.axisLeft(yScale);


    // Draw axes 
    svg.append("g")
        .attr('class', 'x-axis')
        .attr('transform', `translate(0, ${height})`)
        .call(xAxis);

    svg.append("g")
        .attr('class', 'y-axis')
        .call(yAxis);

        // Add the y-axis label
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x", 0 - (height / 2))
        .attr("dy", "1em")
        .attr("text-anchor", "middle")
        .attr("font-size", 17)
        .text("Country");


    // Update axes
    if(svg.selectAll('g.x-axis')._groups[0][0] !== null) svg.selectAll('g.x-axis').remove();
    if(svg.selectAll('g.y-axis')._groups[0][0] !== null) svg.selectAll('g.y-axis').remove();

    svg.append("g")
        .attr('class', 'x-axis')
        .attr('transform', `translate(0, ${height})`)
        .call(xAxis);

    svg.append("g")
        .attr('class', 'y-axis')
        .call(yAxis)



    // Generate the data for a stacked bar chart
    const stackedData = d3.stack().keys(["percent_fully", "percent_partly"])(data)
    


    // Update bars
   // Update bars
    svg.selectAll(".bars").remove();

    svg.append("g")
        .attr("class", "bars")
        .selectAll("g")
        .data(stackedData)
        .join("g")
            .attr("fill", d => cScale(d.key))
        .selectAll("rect")
            .data(d => d)
            .join("rect")
                .attr("y", d => yScale(d.data.location))
                .attr("x", d => xScale(d[0]))
                .attr("width", d => xScale(d[1]) - xScale(d[0]))
                .attr("height",yScale.bandwidth())


    // Draw the labels for bars
    // Draw the labels for bars
    svg.selectAll(".bar-labels").remove();

    svg.append("g")
        .attr("class", "bar-labels")
        .attr("fill", "black")
        .attr("text-anchor", "end")
        .attr("font-family", "sans-serif")
        .attr("font-size", 10)
        .selectAll("g")
        .data(stackedData)
        .join("g")
        .selectAll("text")
        .data(d=>d)
        .join("text")
            .attr("x", d => xScale(d[1]))
            .attr("y", d => yScale(d.data.location) + yScale.bandwidth() / 2)
            .attr("dy", "0.35em")
            .attr("dx", function(d){
                if(d[0]==d.data.percent_fully){
                    return +20
                }else {
                    return -4
                }
            })
            .text(d=>d3.format(".0%")(d[1]-d[0]))


    // Indicate the x-axis label 
    svg.append("text")
        .attr("text-anchor", "end")
        .attr("x", width)
        .attr("y", height + 40)
        .attr("font-family", "sans-serif")
        .attr("font-size", 18)
        .text("Share of people (%)");

}

   // Legend    
    // Legend    
    const legend = d3.select("#legend")
    .append("svg")
    .attr('width', 500)   // Adjust according to your requirements
    .attr('height', 70)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);
    
    legend.append("rect").attr('x', 0).attr('y', 0).attr('width', 12).attr('height', 12).style("fill", "#7bccc4")
    legend.append("rect").attr('x', 0).attr('y', 20).attr('width', 12).attr('height', 12).style("fill", "#2b8cbe")
    legend.append("text").attr("x", 18).attr("y", 10).text("The rate of fully vaccinated people").style("font-size", "15px").attr('alignment-baseline', 'middle');
    legend.append("text").attr("x", 18).attr("y", 30).text("The rate of partially vaccinated people").style("font-size", "15px").attr('alignment-baseline', 'middle');


