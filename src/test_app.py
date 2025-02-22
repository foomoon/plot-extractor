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
        {
            'file': (io.BytesIO(b'\xff\xd8\xff\xe0'),  "input/sample_biphasic.png"),
            "target_color": "#034730",
            "delta": 20,
            "kernel_size": 1,
            "thin": 6,
            "debug": False,
        },
        {
            "origin": (129, 736),         # Expected lower-left point in image coordinates
            "xlim": [0, 10],              # Expected x-axis limits
            "ylim": [-300, 300],          # Expected y-axis limits
            "median_rcs": -3,             # Expected median RCS
        }
    ),
    (
        {
            'file': (io.BytesIO(b'\xff\xd8\xff\xe0'),  "input/sample_noisy_sine_color.png"),
            "target_color": "blue",
            "delta": 20,
            "kernel_size": 1,
            "thin": 2,
            "debug": False,
        },
        {
            "origin": (239, 1439),        # Expected lower-left point in image coordinates
            "xlim": [0, 180],             # Expected x-axis limits
            "ylim": [-30, 30],            # Expected y-axis limits
            "median_rcs": -10,            # Expected median RCS
        }
    ),
    (
        {
            'file': (io.BytesIO(b'\xff\xd8\xff\xe0'),  "input/sample_sine_wave.png"),
            "target_color": "#1F77B4",
            "delta": 20,
            "kernel_size": 1,
            "thin": 2,
            "debug": False,
        },
        {
            "origin": (80, 427),          # Expected lower-left point in image coordinates
            "xlim": [0, 2],               # Expected x-axis limits
            "ylim": [0, 2],               # Expected y-axis limits
            "median_rcs": 1,              # Expected median RCS
        }
    ),
    (
        {
            'file': (io.BytesIO(b'\xff\xd8\xff\xe0'),  "input/sample_stock.png"),
            "target_color": "#1F77B4",
            "delta": 20,
            "kernel_size": 1,
            "thin": 2,
            "debug": False,
        },
        {
            "origin": (80, 427),          # Expected lower-left point in image coordinates
            "xlim": [2000, 3000],         # Expected x-axis limits
            "ylim": [1100, 1600],         # Expected y-axis limits
            "median_rcs": 1300,           # Expected median RCS
        }
    ),
    (
        {
            'file': (io.BytesIO(b'\xff\xd8\xff\xe0'),  "input/sample_rcs.png"),
            "target_color": "blue",
            "delta": 20,
            "kernel_size": 1,
            "thin": 2,
            "debug": False,
        },
        {
            "origin": (62, 365),          # Expected lower-left point in image coordinates
            "xlim": [0, 180],             # Expected x-axis limits
            "ylim": [0, 30],              # Expected y-axis limits
            "median_rcs": 8,              # Expected median RCS
        }
    ),
    (
        {
            'file': (io.BytesIO(b'\xff\xd8\xff\xe0'),  "input/sample_biphasic2.png"),
            "target_color": "grey",
            "delta": 20,
            "kernel_size": 1,
            "thin": 6,
            "debug": False,
        },
        {
            "origin": (377, 1430),        # Expected lower-left point in image coordinates
            "xlim": [0, 10],              # Expected x-axis limits
            "ylim": [-300, 300],          # Expected y-axis limits
            "median_rcs": -3,             # Expected median RCS
        }
    ),
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
    
    # Check xlim and ylim
    assert json_data['xlim'] == expected_output['xlim']
    assert json_data['ylim'] == expected_output['ylim']

    # Check origin is within a small range of expected values
    assert abs(json_data['origin'][0] - expected_output['origin'][0]) < 5
    assert abs(json_data['origin'][1] - expected_output['origin'][1]) < 5

    # Make sure there's at least one data point
    assert len(json_data['data_points']) > 0

    # Check the expected length of data_points
    # assert len(json_data['data_points']) == expected_output['data_points_length'], \
    #        f"Expected data_points length {expected_output['data_points_length']}, got {len(json_data['data_points'])}"