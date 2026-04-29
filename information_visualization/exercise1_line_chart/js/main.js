d3.csv('data/life_expectancy_by_country.csv')
	.then(data => {

        /*

        Process the data here

        */

        const life_expectancy = data.map(d=>d.life_expectancy);
        const min_life_expct = d3.min(life_expectancy);
        const max_life_expct = d3.max(life_expectancy);
        const Diff_expectancy = max_life_expct - min_life_expct;

        const data_sort = data.data_sort((a,b) => d3.desceding(a.life_expectancy - b.life_expectancy))

        const top_5_counties = data_sort.slice(0,5)





        // Draw the line chart 
        drawLineChart(top_5_counties);

	})
 	.catch(error => {
        console.error(error);
        console.error('Error loading the data');
});

function drawLineChart(data){
    const margin = {top: 5, right: 100, bottom: 50, left: 50},
    width = 900 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

    // Define the position of the chart 
    const svg = d3.select("#chart")
    .append("svg")
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
       .append("g")
       .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create a scale for x-axis 
    // const xScale
    const xScale = d3.scaleLinear()
            .domain([d3.min(data, d =>d.year), d3.max(data, d=>d.year)])
            .range([0,width]);

    // Create a scale for y-axis
    // const yScale
    const yScale = d3.scaleLinear()
            .domain([d3.min(data, d =>d.life_expectancy), d3.max(data, d=>d.life_expectancy)])
            .range([height,0]);

    // Define the position of each axis
    const xAxis = d3.axisBottom(xScale);
    const yAxis = d3.axisLeft(yScale);

    // Draw axes 
    const xAxisGroup = svg.append("g")
        .attr('class', 'x-axis')
        .attr('transform', `translate(0, ${height})`)
        .call(xAxis);

    const yAxisGroup = svg.append("g")
        .attr('class', 'y-axis')
        .call(yAxis)

    // Define a scale for color 

    const sScale = d3.scaleOrdinal(d3.schemeCatagory10)
            .domain(data.map(d => d.country))
    
    // Draw the line
    
    const line = d3.line()
            .x(d=>xScale(d.year))
            .y(d=>yScale(d.life_expectancy))
            .curve(d3.curveMonotoneX)

    svg.selectAll(".line")
        .data((data))
        .enter()
        .append("path")
        .attr("class","line")
        .attr("d",d => line(d.values))
        .style("stroke", d=> cScale(d.country));

        // Draw the labels for lines

    svg.selectAll(".label")
        .data(data)
        .enter()
        .append("text")
        .attr("class","label")
        .datum(d => ({country: d.country, value: d}))
    
}
