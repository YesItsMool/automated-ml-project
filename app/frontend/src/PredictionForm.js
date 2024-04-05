import React, { useState } from 'react';
import { Button, TextField, Grid, Typography } from '@mui/material';

function PredictionForm({ onPredict }) {
  const [inputData, setInputData] = useState({
    sepalLength: '',
    sepalWidth: '',
    petalLength: '',
    petalWidth: '',
  });
  const [errors, setErrors] = useState({});
  const [isPredicting, setIsPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setInputData(prevState => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate input data
    const validationErrors = {};
    Object.keys(inputData).forEach(key => {
      if (!inputData[key]) {
        validationErrors[key] = `${key.charAt(0).toUpperCase() + key.slice(1)} is required`;
      }
    });
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsPredicting(true);
    setPredictionResult(null);

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(inputData),
      });

      const data = await response.json();
      if (response.ok) {
        setPredictionResult(data.prediction);
      } else {
        alert('Prediction failed:', data.error);
      }
    } catch (error) {
      console.error('Error during prediction:', error);
      alert('Prediction failed: An error occurred');
    } finally {
      setIsPredicting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container spacing={2}>
        {/* Create TextFields for each input data point */}
        {Object.keys(inputData).map((key, index) => (
          <Grid item xs={6} key={index}>
            <TextField
              name={key}
              label={`${key.charAt(0).toUpperCase() + key.slice(1)}`}
              variant="outlined"
              value={inputData[key]}
              onChange={handleChange}
              error={errors[key] ? true : false}
              helperText={errors[key]}
              required
            />
          </Grid>
        ))}
        <Grid item xs={12}>
          <Button type="submit" variant="contained" color="primary" disabled={isPredicting}>
            {isPredicting ? 'Predicting...' : 'Predict'}
          </Button>
        </Grid>
        {isPredicting && (
          <Grid item xs={12}>
            <Typography variant="body1" align="center">Making prediction...</Typography>
          </Grid>
        )}
        {predictionResult && (
          <Grid item xs={12}>
            <Typography variant="body1" align="center">Prediction Result: {predictionResult}</Typography>
          </Grid>
        )}
      </Grid>
    </form>
  );
}

export default PredictionForm;
