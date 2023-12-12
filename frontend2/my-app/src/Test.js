import { useEffect } from "react";



function Test () {

    useEffect(() => {
        console.log('WebSocket Connected');
        const ws = new WebSocket('ws://localhost:8000/ws')
    
        ws.onmessage = (event) => {
            const newData = JSON.parse(event.data);
            console.log(newData)
        };
    }, []);

    return (
        <div>
            <h1>Test</h1>
        </div>
    )
}


export default Test;