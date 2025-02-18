# Graph Data Extraction

## Overview
This script, `plot_extraction.py`, is designed to extract graphical data from images of plots or graphs using image processing techniques. It utilizes OpenCV for image manipulation and NumPy for numerical operations, with additional support from Matplotlib for visualization.

## Features
- Detects and extracts graph plots from images.
- Uses a convolutional kernel for image smoothing.
- Converts extracted graphical data into numerical values.
- Supports specifying axis range for accurate data extraction.

## Dependencies
Ensure you have the following Python libraries installed before running the script:

```sh
pip install opencv-python numpy matplotlib
```

## Usage
The script can be run directly from the command line. By default, it processes `example_plot.png` and extracts the graph data:

```sh
python plot_extraction.py
```

Alternatively, you can use the `GraphDataExtractor` class in your own scripts:

```python
from plot_extraction import GraphDataExtractor
from find_plot_corners import find_plot_corners
from crop_image import crop_plot

image = cv2.imread('example_plot.png', cv2.IMREAD_GRAYSCALE)

# Find plot corners
origin, top_right = find_plot_corners(image)

# Crop the plot area
image = crop_plot(image, origin, top_right)

graph_extractor = GraphDataExtractor(
    image="path/to/image.png",
    kernel_size=3,
    x_min=0, x_max=180,
    y_min=-50, y_max=40
)

# Run the extractor
graph_extractor.process()

# Save extracted data points as a plot to specified file
graph_extractor.plot_data_points("example_output.png")
```

### Running the Script
If executed as a standalone script, `plot_extraction.py` follows these steps:
1. Loads an image (`example_plot.png`).
2. Finds the plot corners using `find_plot_corners(image)`.
3. Crops the detected plot area using `crop_plot(image, origin, top_right)`.
4. Initializes the `GraphDataExtractor` with predefined axis limits.
5. Extracts and processes the data.

## Modules Used
- `find_plot_corners`: Identifies the corners of the plot in the image.
- `crop_image`: Crops the detected plot area for further processing.

## License
This project is open-source. Feel free to modify and extend it as needed.

