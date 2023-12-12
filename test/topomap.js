// Define electrode positions for 16 channels
const electrodes = [
    { name: "Ch1", x: 100, y: 50 },
    { name: "Ch2", x: 200, y: 50 },
    { name: "Ch3", x: 300, y: 50 },
    { name: "Ch4", x: 50, y: 100 },
    { name: "Ch5", x: 150, y: 100 },
    { name: "Ch6", x: 250, y: 100 },
    { name: "Ch7", x: 350, y: 100 },
    { name: "Ch8", x: 100, y: 150 },
    { name: "Ch9", x: 200, y: 150 },
    { name: "Ch10", x: 300, y: 150 },
    { name: "Ch11", x: 50, y: 200 },
    { name: "Ch12", x: 150, y: 200 },
    { name: "Ch13", x: 250, y: 200 },
    { name: "Ch14", x: 350, y: 200 },
    { name: "Ch15", x: 200, y: 250 },
    { name: "Ch16", x: 300, y: 250 }
];

// Load the data from the JSON file
d3.json("./data.json").then(eegData => {
    const averagedData = eegData.data.map(channelData => d3.mean(channelData));

    // Create SVG element
    const svg = d3.select("#topomap").append("svg")
        .attr("width", 400)
        .attr("height", 300);

    // Define a color scale
    const colorScale = d3.scaleSequential(d3.interpolateCool)
        .domain([d3.min(averagedData), d3.max(averagedData)]);

    // Plot each electrode as a circle
    electrodes.forEach((electrode, i) => {
        svg.append("circle")
            .attr("cx", electrode.x)
            .attr("cy", electrode.y)
            .attr("r", 10) // radius of electrode
            .style("fill", colorScale(averagedData[i]));

        // Optional: Add labels to electrodes
        svg.append("text")
            .attr("x", electrode.x)
            .attr("y", electrode.y + 20) // Adjust label position
            .text(electrode.name)
            .attr("text-anchor", "middle");
    });
}).catch(error => {
    console.error("Error loading the EEG data:", error);
});
