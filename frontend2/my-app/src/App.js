import React, { useState } from 'react';
import FirstPage from './pages/FirstPage';
import SecondPage from './pages/SecondPage';
import './App.css'; // Assuming the CSS is defined here

function App() {
  const [currentPage, setCurrentPage] = useState('first');
  const [animate, setAnimate] = useState(false);

  const handleStart = () => {
    setAnimate(true);
    setTimeout(() => setCurrentPage('second'), 1000); // Match this duration to your animation duration
  };

  return (
    <div>
      {currentPage === 'first' && (
        <FirstPage onStart={handleStart} />
      )}
      {currentPage === 'second' && (
        <div className={animate ? 'fadeIn' : ''}>
          <SecondPage />
        </div>
      )}
    </div>
  );
}

export default App;
