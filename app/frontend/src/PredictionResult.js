// src/PredictionResult.js
import React from 'react';

function PredictionResult({ result }) {
    if (!result) {
        // No prediction made yet or there was an error
        return null;
    }

    // Customize this rendering logic based on how your backend returns results
    const displayResult = `Predicted Class: ${result.class} (Confidence: ${result.confidence}%)`;

    return (
        <div>
            <h3>Prediction Result</h3>
            <p>{displayResult}</p>
            {/* Add additional result details if necessary */}
        </div>
    );
}

export default PredictionResult;
