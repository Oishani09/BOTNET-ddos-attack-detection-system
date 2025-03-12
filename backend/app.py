import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pyshark
import asyncio
import numpy as np
import pandas as pd
from scapy.all import rdpcap

app = Flask(__name__)
CORS(app)

# Load the pre-trained model
model = joblib.load('./randomModel.pkl')

# Load dataset to understand feature structure
dataset = pd.read_csv('./D2.csv')  # Update with the actual path to your dataset
feature_columns = dataset.columns.tolist()

# Function to extract features from pcap file using PyShark
def extract_features_from_pcap(pcap_file):
    # Create a new event loop to prevent asyncio issues
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    cap = pyshark.FileCapture(pcap_file, only_summaries=True, eventloop=loop)
    
    # Initialize feature dictionary based on dataset columns
    features = {feature: 0 for feature in feature_columns}
    
    # Handle initial values for min-type features that should start high
    min_initial_features = [
        "Fwd Packet Length Min", "Bwd Packet Length Min", 
        "Flow IAT Min", "Fwd IAT Min", "Bwd IAT Min", 
        "Min Packet Length", "Active Min", "Idle Min"
    ]
    
    for min_feature in min_initial_features:
        features[min_feature] = float('inf')

    # Process packets and extract features
    for packet in cap:
        try:
            # Example logic for updating feature values; adapt for specific needs of each feature
            features["Flow Duration"] += 1  # Increment duration for each packet
            
            # Example for Fwd/Bwd packet counts based on packet direction
            if hasattr(packet, 'ip'):
                features["Total Fwd Packets"] += 1 if packet.ip.src else 0
                features["Total Backward Packets"] += 1 if packet.ip.dst else 0

            # Example for calculating min and max packet lengths
            packet_length = int(packet.length)
            features["Max Packet Length"] = max(features["Max Packet Length"], packet_length)
            features["Min Packet Length"] = min(features["Min Packet Length"], packet_length)

            # Update other feature aggregations as per dataset requirements
            # Add additional logic for calculating averages, totals, flags, etc.
        
        except AttributeError:
            pass  # Handle cases where packet attributes might be missing

    # Finalize any feature calculations that need averages, e.g., mean packet length
    if features["Flow Duration"] > 0:
        features["Packet Length Mean"] = features["Total Length of Fwd Packets"] / features["Flow Duration"]

    # Convert features dictionary to an ordered feature vector for model compatibility
    feature_vector = np.array([features[feature] for feature in feature_columns]).reshape(1, -1)
    cap.close()
    loop.close()  # Close the event loop
    
    return feature_vector

@app.route('/api/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.pcap'):
        return jsonify({'error': 'Invalid file type. Please upload a .pcap file.'}), 400
    
    # Save the uploaded file to a temporary location
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pcap')
    file.save(temp_file.name)  # Save the uploaded file to the temp location

    # Extract features from the uploaded pcap file
    features = extract_features_from_pcap(temp_file.name)

    # Model prediction (1 for attack detected, 0 for no attack detected)
    prediction = model.predict(features)
    
    # Convert prediction to "Yes" or "No" based on the result
    result = "Your .pcap file has no ddos attack!" if prediction[0] == 1 else "it has ddos attack!"
    
    # Clean up the temporary file after use
    os.remove(temp_file.name)

    return jsonify({'prediction': result})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
