import React, { useState, useEffect } from 'react';

const DataDisplay: React.FC = () => {
  const [data, setData] = useState<any[]>([]); // Replace 'any' with a more specific type for your data

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws'); // Adjust URL as needed
    ws.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setData(currentData => [...currentData, newData]);
    };

    return () => {  
      ws.close();
    };
  }, []);

  return (
    <div>
      <h2>EEG Data:</h2>
      {data.map((datum, index) => (
        <div key={index}>
          {/* Render your data here */}
          {JSON.stringify(datum)}
        </div>
      ))}
    </div>
  );
};

export default DataDisplay;
