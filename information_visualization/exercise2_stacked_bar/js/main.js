// Load the CSV data
d3.csv('data/owid-covid-data.csv')
	.then(data => {
        // Process the data
        const processedData = processData(data);
        // Draw the stacked bar chart
        drawBarChart(processedData);
	})
 	.catch(error => {
         console.error(error);
	});

// processData function: filters and formats the data for visualization
function processData(data) {
    // Get the most recent data for each country
    const latestData = {};
    data.forEach(d => {
        if (!latestData[d.location] || latestData[d.location].date < d.date) {
            latestData[d.location] = d;
        }
    });

    // Calculate percentages and sort by the top 15 countries
    const processedData = Object.values(latestData)
        .map(d => ({
            country: d.location,
            population: +d.population,
            fullyVaccinated: +d.people_fully_vaccinated,
            partiallyVaccinated: +d.people_vaccinated - +d.people_fully_vaccinated,
        }))
        .filter(d => {
            const totalVaccinated = d.partiallyVaccinated + d.fullyVaccinated;
            return totalVaccinated / d.population <= 1;
        })
        .sort((a, b) => (b.partiallyVaccinated + b.fullyVaccinated) / b.population - (a.partiallyVaccinated + a.fullyVaccinated) / a.population)
        .slice(0, 15)
        .map(d => ({
            ...d,
            fullyVaccinatedPercentage: (d.fullyVaccinated / d.population) * 100,
            partiallyVaccinatedPercentage: (d.partiallyVaccinated / d.population) * 100,
        }));

    return processedData;
}

// drawBarChart function: creates a horizontal stacked bar chart using D3.js
function drawBarChart(data) {
    // Set the chart dimensions and margins
    const margin = {top: 5, right: 30, bottom: 50, left: 100},
    width = 800 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

    // Define the position of the chart 
    const svg = d3.select("#chart")
       .append("svg")
       .attr('width', width + margin.left + margin.right)
       .attr('height', height + margin.top + margin.bottom)
          .append("g")
          .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create a scale for x-axis 
    const xScale = d3.scaleLinear()
        .domain([0, 100])
        .range([0, width]);

    // Create a scale for y-axis
    const yScale = d3.scaleBand()
        .domain(data.map(d => d.country))
        .range([0, height])
        .padding(0.3);

    // Define the position of each axis
    const xAxis = d3.axisBottom(xScale);
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

            // Define a scale for color
    const cScale = d3.scaleOrdinal()
        .domain(["fullyVaccinatedPercentage", "partiallyVaccinatedPercentage"])
        .range(["#7bccc4", "#2b8cbe"]);

    // Generate the data for a stacked bar chart
    const stackedData = d3.stack()
        .keys(["fullyVaccinatedPercentage", "partiallyVaccinatedPercentage"])
        (data);

    // Draw the bars
    const barGroups = svg.selectAll(".bar-group")
        .data(stackedData)
        .join("g")
        .attr("class", "bar-group")
        .attr("fill", d => cScale(d.key));

    barGroups.selectAll("rect")
        .data(d => d)
        .join("rect")
        .attr("x", d => xScale(d[0]))
        .attr("y", d => yScale(d.data.country))
        .attr("width", d => xScale(d[1]) - xScale(d[0]))
        .attr("height", yScale.bandwidth());

    // Draw the labels for bars
    barGroups.selectAll("text")
        .data(d => d)
        .join("text")
        .attr("x", d => xScale(d[1]) - 5)
        .attr("y", d => yScale(d.data.country) + yScale.bandwidth() / 2)
        .attr("dy", ".35em")
        .text(d => d3.format(".1f")(d[1] - d[0]))
        .attr("text-anchor", "end")
        .attr("fill", "white");

    // Indicate the x-axis label
    svg.append("text")
        .attr("text-anchor", "end")
        .attr("x", width)
        .attr("y", height + 40)
        .attr("font-size", 17)
        .text("Share of people (%)");

    // Legend
    const legend = d3.select("#legend")
        .append("svg")
        .attr('width', width)
        .attr('height', 70)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

    legend.append("rect").attr('x', 0).attr('y', 18).attr('width', 12).attr('height', 12).style("fill", "#7bccc4")
    legend.append("rect").attr('x', 0).attr('y', 36).attr('width', 12).attr('height', 12).style("fill", "#2b8cbe")
    legend.append("text").attr("x", 18).attr("y", 18).text("The rate of fully vaccinated people").style("font-size", "15px").attr('text-anchor', 'start').attr('alignment-baseline', 'hanging');
    legend.append("text").attr("x", 18).attr("y", 36).text("The rate of partially vaccinated people").style("font-size", "15px").attr('text-anchor', 'start').attr('alignment-baseline', 'hanging');
}
