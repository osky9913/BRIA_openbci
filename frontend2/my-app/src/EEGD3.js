import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

const colorScale = d3.scaleOrdinal(d3.schemeSpectral);
const channelOffset = 500 / 10; 



function EEGD3() {
  const ws = useRef(null);
  const dataRef = useRef(Array.from({ length: 16 }, () => Array(1).fill(0)));
  const svgRef = useRef(null);
  const [width, height] = [600, 400]; // Width and height of the chart
  const margin = { top: 20, right: 20, bottom: 30, left: 40 };
  const sfqs = 125; // Sampling frequency
  const dataWindow = sfqs * 1;

  // Initialize D3 chart
  useEffect(() => {
    createChart();
  }, []);

  // WebSocket connection and data handling
  useEffect(() => {
    if (!ws.current) {
      ws.current = new WebSocket("ws://localhost:8000/ws");
      ws.current.onopen = () => console.log("WebSocket Connected");

      ws.current.onmessage = (event) => {
        if (event.data) {
          let newData = JSON.parse(event.data);
          if (newData.length === 0) return;

          dataRef.current = dataRef.current.map((subArray, index) => {
            let updatedArray = [...subArray, ...(newData[index] || [])];
            return updatedArray.slice(-dataWindow); // Keep only the latest 5 seconds of data
          });

          updateChart();
        }
      };
    }

    // Cleanup function
  }, []);

  // Function to initialize the D3 chart
  // Function to initialize the D3 chart
  const createChart = () => {
    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    // Add scales and axes here
    const xScale = d3
      .scaleLinear()
      .domain([0, dataWindow])
      .range([margin.left, width - margin.right]);

    const yScale = d3
      .scaleLinear()
      .domain([-1, 1]) // Assuming EEG data range
      .range([height - margin.bottom, margin.top]);

    svg
      .append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(xScale));

    svg
      .append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(yScale));
  };

  // Function to update the chart with new data
  const updateChart = () => {
    const svg = d3.select(svgRef.current);

    const xScale = d3
      .scaleLinear()
      .domain([0, dataWindow])
      .range([margin.left, width - margin.right]);

    const yScales = dataRef.current.map(channelData => 
        d3.scaleLinear()
          .domain([-1, 1]) // Adjust if different ranges per channel are needed
          .range([height - margin.bottom, margin.top])
    );

    dataRef.current.forEach((channelData, index) => {
        const yScale = yScales[index];
        const line = d3.line()
            .x((d, i) => xScale(i))
            .y((d) => yScale(d))
            .curve(d3.curveBasis);

        svg
          .selectAll(`.line-channel-${index}`)
          .data([channelData])
          .join("path")
          .attr("class", `line line-channel-${index}`)
          .attr("d", line)
          .attr("fill", "none")
          .attr("stroke", colorScale(index)) // Use a color scale or specific colors
          .attr("transform", `translate(0,${index * channelOffset})`); // Offset each line
    });
};

  return (
    <div>
      <svg ref={svgRef}></svg>
    </div>
  );
}

export default EEGD3;
