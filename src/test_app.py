# import io
# import pytest
# from extractor_app import app

# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     # Disable CSRF checks or any other production middleware if needed
#     with app.test_client() as client:
#         yield client

# def test_extract_no_file(client):
#     # No file provided in POST data
#     response = client.post('/extract', data={})
#     json_data = response.get_json()
#     assert response.status_code == 400
#     assert 'error' in json_data
#     assert json_data['error'] == 'No file part'

# def test_extract_empty_filename(client):
#     # Provide an empty filename
#     data = {
#         'file': (io.BytesIO(b"dummy content"), '')
#     }
#     response = client.post('/extract', data=data, content_type='multipart/form-data')
#     json_data = response.get_json()
#     assert response.status_code == 400
#     assert json_data.get('error') == 'No selected file'

# def test_extract_success(client):
#     # Create a fake image file (for test purposes, a small byte string)
#     fake_image_content = b'\xff\xd8\xff\xe0'  # Minimal JPEG header bytes
#     # read a real image from input/sample_noisy_sine_color.png
#     with open('input/sample_noisy_sine_color.png', 'rb') as f:
#         fake_image_content = f.read()

#     data = {
#         'file': (io.BytesIO(fake_image_content), 'test.jpg'),
#         # Provide all required form fields with valid values
#         'target_color': '#0000ff',
#         'delta': '20',
#         'kernel_size': '1',
#         'thin': '3',
#         'dpi': '300',
#         'classification': 'SAMPLE',
#         'title': 'Test Plot',
#         'x_label': 'X Axis',
#         'y_label': 'Y Axis',
#         'isMedian': 'True',
#         # To simulate manual axis limits (if needed), comment out or remove detect_axes,
#         # For automatic axis detection set detect_axes to any value.
#         'detect_axes': 'on'
#     }
#     response = client.post('/extract', data=data, content_type='multipart/form-data')
#     json_data = response.get_json()
#     # Expect a 200 status code and JSON response that includes expected keys.
#     assert response.status_code == 200
#     # The exact keys depend on what run() returns. For example:
#     assert 'data_points' in json_data
#     # If your output may include a median value, check for it as well.
#     # Example (if run() returns a median_rcs key):
#     assert 'median_rcs' in json_data
#     # Assert a median value range
#     assert 0 <= json_data['median_rcs'] <= 1

import io
import os
import math
import pytest
from extractor_app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_extract_no_file(client):
    # No file provided in POST data
    response = client.post('/extract', data={})
    json_data = response.get_json()
    assert response.status_code == 400
    assert 'error' in json_data
    assert json_data['error'] == 'No file part'

def test_extract_empty_filename(client):
    # Provide an empty filename
    data = {
        'file': (io.BytesIO(b"dummy content"), '')
    }
    response = client.post('/extract', data=data, content_type='multipart/form-data')
    json_data = response.get_json()
    assert response.status_code == 400
    assert json_data.get('error') == 'No selected file'

# Parameterized test: each tuple contains (form_fields, expected_output)
@pytest.mark.parametrize("form_fields, expected_output", [
    (
        # Input form fields for test extraction 
        # (we pass dummy data which is replaced with real image data in the associated path)
        {
            'file': (io.BytesIO(b'\xff\xd8\xff\xe0'), 'input/sample_noisy_sine_color.png'),
            'target_color': '#0000ff',
            'delta': '20',
            'kernel_size': '1',
            'thin': '3',
            'dpi': '300',
            'classification': 'SAMPLE',
            'title': 'Test Plot',
            'x_label': 'X Axis',
            'y_label': 'Y Axis',
            'isMedian': 'True',
            'detect_axes': 'True',
            'debug': 'False'
        },
        # Expected output: adjust these expected values as appropriate for your app.
        {
            'median_rcs': -10,        # Expected median (approximate)
            'data_points_length': 10  # Expected number of data points in the response
        }
    ),
    # You can add additional parameter sets here.
])
def test_extract_parameterized(client, form_fields, expected_output):
    # get the filename from the form_fields
    filename = form_fields['file'][1]
    # read a real image from filename
    with open(filename, 'rb') as f:
        fake_image_content = f.read()
    # Get the basename of the filename
    filename = os.path.basename(filename)
    # Set the file content to the image file
    form_fields['file'] = (io.BytesIO(fake_image_content), filename)
    # Create a fake image file (for test purposes, a small byte string)
    response = client.post('/extract', data=form_fields, content_type='multipart/form-data')
    json_data = response.get_json()
    
    # Verify HTTP 200 status code
    assert response.status_code == 200

    # Check that the expected keys are in the response
    assert 'median_rcs' in json_data
    assert 'data_points' in json_data

    # Use math.isclose for floating point comparison of median_rcs
    assert math.isclose(json_data['median_rcs'], expected_output['median_rcs'], rel_tol=1e-1), \
           f"Expected median {expected_output['median_rcs']}, got {json_data['median_rcs']}"

    # Check the expected length of data_points
    # assert len(json_data['data_points']) == expected_output['data_points_length'], \
    #        f"Expected data_points length {expected_output['data_points_length']}, got {len(json_data['data_points'])}"