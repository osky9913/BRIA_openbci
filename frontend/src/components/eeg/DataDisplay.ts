import { useEffect, useState } from "react";

function DataDisplay() {
    const [data, setData] = useState([]);
  
    useEffect(() => {
      const websocket = new WebSocket('ws://localhost:8000/ws'); // Adjust the URL as needed
      websocket.onmessage = (event) => {
        const newData = JSON.parse(event.data);
        setData((prevData) => [...prevData, newData]);
      };
  
      return () => websocket.close();
    }, []);
  
    return (
      <div>
        <h2>EEG Data:</h2>
        {/* Render your data here */}
        {data.map((datum, index) => (
          <div key={index}>{JSON.stringify(datum)}</div>
        ))}
      </div>
    );
  }
  
  export default DataDisplay;