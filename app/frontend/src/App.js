// src/App.js

import React, { useState } from 'react';
import Navigation from './Navigation';
import MyGridComponent from './MyGridComponent';
import DatasetUpload from './DatasetUpload';
import TrainModelButton from './TrainModelButton';
import PredictionForm from './PredictionForm';
import PredictionResult from './PredictionResult';

function App() {
  const [uploadedFilename, setUploadedFilename] = useState('');
  const [predictionResult, setPredictionResult] = useState(null);


  const handleFileUploadSuccess = (filename) => {
    setUploadedFilename(filename);
  };

  return (
    <div>
      <h1>Machine Learning Dashboard</h1>
      <MyGridComponent />
      <Navigation />
      <DatasetUpload onSuccess={handleFileUploadSuccess} />
      {uploadedFilename && <TrainModelButton filename={uploadedFilename} />}
      <PredictionForm onPredict={setPredictionResult} />
      <PredictionResult result={predictionResult} />
    </div>
  );
}

export default App;
