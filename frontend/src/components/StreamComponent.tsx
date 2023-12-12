import React from 'react';

interface StreamControlProps {
  onStreamPrepared: () => void;
}

const StreamControl: React.FC<StreamControlProps> = ({ onStreamPrepared }) => {
  const prepareStream = async () => {
    try {
      await fetch('http://localhost:8000/prepare_stream'); // Adjust URL as needed
      onStreamPrepared();
    } catch (error) {
      console.error('Error preparing stream:', error);
    }
  };

  return <button onClick={prepareStream}>Prepare Stream</button>;
};

export default StreamControl;
