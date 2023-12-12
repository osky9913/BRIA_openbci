import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface LineGraphProps {
  data: number[][]; // Assuming each sub-array is a series for the line chart
}

const LineGraph: React.FC<LineGraphProps> = ({ data }) => {
  const d3Container = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (data.length === 0 || !d3Container.current) return;

    // Define a color scale
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

    const svg = d3.select(d3Container.current);

    // Set the dimensions and margins of the graph
    const margin = { top: 10, right: 30, bottom: 30, left: 60 };
    const width = 460 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Append the svg object to the body of the page
    svg.selectAll("*").remove(); // Clear svg content before adding new elements
    const g = svg.append("g")
                 .attr("transform", `translate(${margin.left},${margin.top})`);

    // Add X axis
    const x = d3.scaleLinear()
                .domain([0, d3.max(data, d => d.length)])
                .range([0, width]);
    g.append("g")
     .attr("transform", `translate(0,${height})`)
     .call(d3.axisBottom(x));

    // Add Y axis
    const y = d3.scaleLinear()
                .domain([0, d3.max(data.flat()) as number]) // Use the max value from all series
                .range([height, 0]);
    g.append("g").call(d3.axisLeft(y));

    // Draw the line
    const line = d3.line<number>()
                  .x((d, i) => x(i))
                  .y(y);
    
    data.forEach((series, i) => {
      g.append("path")
       .datum(series)
       .attr("fill", "none")
       .attr("stroke", colorScale(i.toString())) // Use the color scale for stroke
       .attr("stroke-width", 0.3)
       .attr("d", line);
    });

    // If needed, define a transition for the line update

  }, [data]); // Redraw the graph when the data changes

  return (
    <svg
      className="d3-component"
      width="460"
      height="400"
      ref={d3Container}
    />
  );
};

export default LineGraph;
