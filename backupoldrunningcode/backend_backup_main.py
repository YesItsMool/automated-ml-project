# app/backend/main.py

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
import logging
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

scaler = StandardScaler()

# Configuration
UPLOAD_FOLDER = 'data/uploads'
MODEL_FOLDER = 'models'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MODEL_FOLDER'] = MODEL_FOLDER

# Ensure the upload and model folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_classification(y):
    # Simple heuristic: if the target variable is integer and has a limited number of unique values, assume classification
    return y.dtype == np.int64 and len(np.unique(y)) < 20

@app.route('/')
def index():
    return "The Flask server is running!"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logging.info(f'File {filename} uploaded successfully.')
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/train', methods=['POST'])
def train_model():
    data_filename = request.json.get('filename')
    if not data_filename or not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], data_filename)):
        return jsonify({'error': 'File not found'}), 404

    try:
        data = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
        if data.empty or data.shape[1] < 2:
            return jsonify({'error': 'Invalid or insufficient data'}), 400
        
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        model = LogisticRegression(max_iter=200)
        model.fit(X_scaled, y_encoded)

        model_filename = 'model.pkl'
        model_path = os.path.join(app.config['MODEL_FOLDER'], model_filename)
        joblib.dump(model, model_path)

        le_filename = 'label_encoder.pkl'
        le_path = os.path.join(app.config['MODEL_FOLDER'], le_filename)
        joblib.dump(le, le_path)

        scaler_filename = 'scaler.pkl'
        scaler_path = os.path.join(app.config['MODEL_FOLDER'], scaler_filename)
        joblib.dump(scaler, scaler_path)

        return jsonify({'message': 'Model trained successfully', 'model_path': model_path}), 200
    except Exception as e:
        app.logger.error(f'An error occurred during training: {e}')
        return jsonify({'error': 'An error occurred during training'}), 500

    

@app.route('/predict', methods=['POST'])
def predict():
    # Load the trained model, label encoder, and scaler state
    model_path = os.path.join(app.config['MODEL_FOLDER'], 'model.pkl')
    le_path = os.path.join(app.config['MODEL_FOLDER'], 'label_encoder.pkl')

    if not os.path.exists(model_path) or not os.path.exists(le_path):
        return jsonify({'error': 'Model or Label Encoder not found'}), 404

    model = joblib.load(model_path)
    le = joblib.load(le_path)

    input_data = request.json.get('data')
    if not input_data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        feature_names = ['sepal.length', 'sepal.width', 'petal.length', 'petal.width']
        input_df = pd.DataFrame([input_data], columns=feature_names)

        # Load and use the saved scaler to transform the input data
        scaler_path = os.path.join(app.config['MODEL_FOLDER'], 'scaler.pkl')
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
            input_scaled = scaler.transform(input_df)
        else:
            return jsonify({'error': 'Scaler not found'}), 404

        prediction = model.predict(input_scaled)
        class_prediction = le.inverse_transform(prediction)
        return jsonify({'prediction': class_prediction.tolist()}), 200
    except Exception as e:
        app.logger.error(f'An error occurred during prediction: {e}')
        return jsonify({'error': 'An error occurred during prediction'}), 500


if __name__ == '__main__':
    app.run(debug=True)
