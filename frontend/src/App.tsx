import { useState } from 'react'
import UpdateElectron from '@/components/update'
import logoVite from './assets/logo-vite.svg'
import logoElectron from './assets/logo-electron.svg'
import './App.css'

console.log('[App.tsx]', `Hello world from Electron ${process.versions.electron}!`)

function App() {
  const [streaming, setStreaming] = useState(false);

  const handleStreamStart = async () => {
    const response = await fetch('/start_stream'); // Adjust the URL as needed
    const data = await response.json();
    if (data.status === 'Stream started') {
      setStreaming(true);
    }
  };

  return (
    <div className="App">
      {!streaming && <button onClick={handleStreamStart}>Start Stream</button>}
      {/* Data Display Component will go here */}
    </div>
  );
}
export default App