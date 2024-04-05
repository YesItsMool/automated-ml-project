import React, { useState } from 'react';
import { Button, LinearProgress } from '@mui/material';

function TrainModelButton({ filename }) {
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleTrainModel = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/train', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename }),
      });

      if (response.ok) {
        // Training initiated, update progress
        const reader = response.body.getReader();
        let receivedLength = 0;
        let chunks = [];
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          chunks.push(value);
          receivedLength += value.length;
          setProgress((receivedLength / response.headers.get('content-length')) * 100);
        }
        setIsLoading(false);
        alert(`Model training initiated for the file: ${filename}`);
      } else {
        const data = await response.json();
        alert(`Failed to start model training: ${data.message}`);
        setIsLoading(false);
      }
    } catch (error) {
      alert('Failed to start model training. Please try again.');
      console.error('Training Model Error:', error);
      setIsLoading(false);
    }
  };

  return (
    <div>
      <Button
        variant="contained"
        color="secondary"
        onClick={handleTrainModel}
        disabled={isLoading}
      >
        {isLoading ? 'Training...' : 'Train Model'}
      </Button>
      {isLoading && <LinearProgress variant="determinate" value={progress} />}
    </div>
  );
}

export default TrainModelButton;
