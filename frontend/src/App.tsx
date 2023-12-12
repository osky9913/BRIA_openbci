import React, { useState } from 'react';
import StreamControl from './components/StreamComponent';
import EEGPlot from './components/EEGPlot';
import LineGraph from './components/LineGraph';


const MAX_SAMPLES = 1000;
const INITIAL_EEG_DATA_LENGTH = 16; // Number of sub-arrays
const INITIAL_SUBARRAY_LENGTH = 1; // Length of each sub-array, assuming you want them initially empty
const initialEegData = Array.from({ length: INITIAL_EEG_DATA_LENGTH }, () => 
Array(INITIAL_SUBARRAY_LENGTH).fill(0)
);

const App: React.FC = () => {
  

  const [allEegData, setAllEegData] = useState<number[][]>(initialEegData);
  const [showPlot, setShowPlot] = useState(false);
  const [lineGraphData, setLineGraphData] = useState<number[][]>(initialEegData);

  const [websocket, setWebsocket] = useState<WebSocket | null>(null);


  const handleStreamPrepared = () => {
    // Create a new WebSocket connection
    console.log('WebSocket Connected');
    const ws = new WebSocket('ws://localhost:8000/ws'); // Adjust URL as needed

    ws.onmessage = (event) => {
      let  newData = JSON.parse(event.data);
      newData = newData["data"][0] // newData are now in chape [n_chanel, n_sample]
      console.log({newData})
      console.log({allEegData})

      setAllEegData(prevData => {
        // Assuming newData is an array of arrays and you want to merge it with the existing data
        // You can adjust this logic as needed};
        for (let i = 0; i < newData.length; i++) {
          prevData[i].push(... newData[i]); 
          }
        
        return prevData;
      });
      setLineGraphData((prevData) => {
        // Update line graph data here
        const updatedData = prevData.map((channelData, i) => {
          const newChannelData = channelData.concat(newData[i]);
          return newChannelData.slice(-MAX_SAMPLES); // Keep only the last MAX_SAMPLES
        });
  
        return updatedData;
      });
      


    };
    

    ws.onclose = () => {
        console.log('WebSocket Disconnected');
        setWebsocket(null);
    };

    ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
    };

    setWebsocket(ws);
};


  const togglePlot = () => {
    setShowPlot(!showPlot);
  };

  return (
    <div className="App">
      <StreamControl onStreamPrepared={handleStreamPrepared} />
      <button onClick={togglePlot}>{showPlot ? 'Hide Plot' : 'Show Plot'}</button>
      {showPlot && <LineGraph data={lineGraphData} />}
    </div>
  );
};

export default App;
