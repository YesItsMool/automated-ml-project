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
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
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
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
    if not data_filename or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        # Load the dataset
        data = pd.read_csv(file_path)
        if data.empty or data.shape[1] < 2:
            return jsonify({'error': 'Invalid or insufficient data'}), 400

        # Separate features and target
        X = data.iloc[:, :-1]
        y = data.iloc[:, -1]

        # Initialize scaler and label encoder
        scaler = StandardScaler()
        le = LabelEncoder()

        # Check if the target variable is categorical
        if y.dtype == 'object':
            y = le.fit_transform(y)
            model = LogisticRegression(max_iter=200)
            is_classification = True
        else:
            model = LinearRegression()
            is_classification = False

        # Scale features
        X_scaled = scaler.fit_transform(X)

        # Split the dataset into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

        # Train the model
        model.fit(X_train, y_train)

        # Evaluation
        if is_classification:
            y_pred = model.predict(X_test)
            score = accuracy_score(y_test, y_pred)
            metric = 'accuracy'
        else:
            y_pred = model.predict(X_test)
            score = mean_squared_error(y_test, y_pred)
            metric = 'mean_squared_error'

        # Save the trained model and scaler
        model_filename = 'model.pkl'
        model_path = os.path.join(app.config['MODEL_FOLDER'], model_filename)
        joblib.dump(model, model_path)

        scaler_filename = 'scaler.pkl'
        scaler_path = os.path.join(app.config['MODEL_FOLDER'], scaler_filename)
        joblib.dump(scaler, scaler_path)

        # If classification, save the label encoder
        if is_classification:
            le_filename = 'label_encoder.pkl'
            le_path = os.path.join(app.config['MODEL_FOLDER'], le_filename)
            joblib.dump(le, le_path)

        # Send back a success response with evaluation metrics
        return jsonify({
            'message': 'Model trained successfully',
            'model_path': model_path,
            'evaluation': {metric: score}
        }), 200
    except Exception as e:
        app.logger.error(f'An error occurred during training: {str(e)}')
        return jsonify({'error': str(e)}), 500
    

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
