from flask import Flask, request, jsonify
import cv2
import numpy as np
from ..src.graph_data_extractor import GraphDataExtractor

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Read the image file
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # Initialize the extractor and process the image
    extractor = GraphDataExtractor()
    extractor.load_image(image)

    # Do some other stuff

    #

    # Extract data points
    data_points = extractor.extract_data_points()
    
    return jsonify({'data_points': data_points.tolist()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)