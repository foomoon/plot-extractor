import os
from flask import Flask, request, jsonify, render_template, url_for
import cv2
import numpy as np
from run import main as run
from types import SimpleNamespace
from pdf_extract import extract as extract_images_from_pdf
from pdf_extract import save_images_to_pdf



app = Flask(__name__)

# @app.route('/')
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/v2')
def index2():
    return render_template("v2.html")

@app.route('/pdf')
def pdf():
    return render_template("pdf.html")

@app.route('/extractpdf', methods=['POST'])
def extractpdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    #save the file
    output_folder = "static/images/pdf"
    os.makedirs(output_folder, exist_ok=True)
    # empty the folder (BE CAREFUL!!!)
    os.system(f"rm -rf {output_folder}/*")
    file_path = f"{output_folder}/{file.filename}"
    file.save(file_path)
    
    print(f"Extracting images from {file_path} to {output_folder}")
    result = extract_images_from_pdf(file_path, output_folder, 100)

    # remove original pdf
    print(f"Cleaning up: Removing original PDF")
    os.system(f"rm -rf {file_path}")

    print(f"Saving images to PDF")
    save_images_to_pdf(result['images_saved'], output_folder)

    # zip the images and save the zip file to the output folder
    print(f"Zipping images to {output_folder}")
    zip_path = f"{output_folder}/images.zip"
    os.system(f"zip -r {zip_path} {output_folder}")

    # remove all of the images
    print(f"Cleaning up: Removing images")
    os.system(f"rm -rf {output_folder}/*.png")

    return jsonify(result)
    # return jsonify({'message': 'PDF images extracted successfully'})

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

    # Get parameters from the form (or use default values if missing)
    target_color = request.form.get('target_color', '#034730')
    delta = int(request.form.get('delta', 20))
    kernel_size = int(request.form.get('kernel_size', 1))
    thin = int(request.form.get('thin', 6))
    dpi = int(request.form.get('dpi', 300))
    classification = request.form.get('classification', 'SAMPLE')
    title = request.form.get("title", "Example Figure")
    x_label = request.form.get("x_label", "X Axis")
    y_label = request.form.get("y_label", "Y Axis")
    isMedian = request.form.get("isMedian", True)
    debug = request.form.get("debug", False)

    # If images is None, then the file was not a valid image
    if image is None:
        return jsonify({'error': 'Invalid image file'}), 400

    # Check the checkbox: if it is unchecked, then get axis limits;
    # note: when a checkbox is checked its value is submitted.
    detect_axes = request.form.get('detect_axes', True)
    # If detect_axes is None, then it was unchecked (user wants manual limits)
    if detect_axes is None:
        try:
            # Parse the axis limits from the form
            x_min = float(request.form.get('x_min'))
            x_max = float(request.form.get('x_max'))
            y_min = float(request.form.get('y_min'))
            y_max = float(request.form.get('y_max'))
            x_lim = [x_min, x_max]
            y_lim = [y_min, y_max]
        except (TypeError, ValueError):
            x_lim = None
            y_lim = None
    else:
        # When the checkbox is checked, we let the code detect axes automatically
        x_lim = None
        y_lim = None

    settings = {
        "target_color": target_color,
        "delta": delta,
        "kernel_size": kernel_size,
        "thin": thin,
        "debug": debug,
        "output_folder": "static/images",
        "classification": classification,
        'dpi': dpi,
        "x_lim": x_lim,
        "y_lim": y_lim,
        "title": title,
        "x_label": x_label,
        "y_label": y_label,
        "isMedian": isMedian
    }

    # Convert the dictionary to an object with attributes
    args = SimpleNamespace(**settings)

    result = run(image, args)
    
    if hasattr(result["data_points"], "tolist"):
        result["data_points"] = result["data_points"].astype(float).tolist()
    
    if hasattr(result["median_rcs"], "item"):
        result["median_rcs"] = float(result["median_rcs"].item())

    # Include the extracted_image URL in the result if applicable
    # result["extracted_image"] = url_for('static', filename='images/extracted-image.png')
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)