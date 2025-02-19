import os
import argparse
import matplotlib.pyplot as plt
from graph_data_extractor import GraphDataExtractor
from extract_axes import extract_axes_labels
from utils import calculate_median_rcs
import csv

from sample_figure import generate_sample_figure, plot_median

import numpy as np

def validate_limits(xlim):
  """Validates the x and y limits."""
  if xlim[0] >= xlim[1]:
      print(f"Invalid axis limits: {xlim}")
      return False
  if xlim[1] - xlim[0] < 1:
      print(f"Invalid axis limits: {xlim}")
      return False
  return True

def save_to_csv(data_points, csv_filename):
  # Save data_points to a CSV file in the output_folder
  with open(csv_filename, "w", newline="") as csvfile:
      writer = csv.writer(csvfile)
      # Write header if desired
      writer.writerow(["x", "y"])
      # Write each data point (assumes each data_point is an iterable with x and y values)
      writer.writerows(data_points)

  print(f"Data points saved to {csv_filename}")


def main(args):
    # Settings and paths from command line arguments
    image_path = args.image_path
    target_color = args.target_color
    delta = args.delta
    debug = args.debug
    output_folder = args.output
    csv_folder = "output/results"

    # Initialize extractor and load image
    extractor = GraphDataExtractor()
    extractor.load_image(image_path, target_color=target_color, delta=delta)
    extractor.set_kernel_size(args.kernel_size)
    extractor.set_thin(args.thin)

    # Get original area and crop if necessary
    original_image_area = extractor.get_image_area()
    extractor.crop_to_plot_area()
    min_plot_area = original_image_area * 0.8
    plot_area = extractor.get_image_area()
    
    if plot_area < min_plot_area:
        extractor.load_image(image_path, target_color=target_color, delta=delta)
        print(f"Reloaded image area = {extractor.get_image_area()}\n")

    # Find plot corners (origin) and extract axes labels
    origin, _ = extractor.find_corners(debug=debug)

    if args.debug:
      print(image_path)
      print(f"\nOrigin found at: {origin}\n")
    image = extractor.get_image()
    x_axis, y_axis = extract_axes_labels(image, origin, DEBUG=args.debug, factor=0.004)

    # Convert to grayscale after isolating target color
    extractor.filter_to_gray(target_color, delta=delta)
    
    if not x_axis:
        print("No x axis found, using default")
        x_axis = [0, 180]
    if not y_axis:
        print("No y axis found, using default")
        y_axis = [-30, 30]

    xlim = [x_axis[0], x_axis[-1]]
    ylim = [y_axis[0], y_axis[-1]]

    # xlim = [min(x_axis), max(x_axis)]
    # ylim = [min(y_axis), max(y_axis)]

    if args.debug:
      print("Extracted Axes")
      print(f"  X-axis: {x_axis}")
      print(f"  Y-axis: {y_axis}")

    if not validate_limits(xlim):
        print("Using default x limits")
        xlim = [0, 180]
    if not validate_limits(ylim):
        print("Using default y limits")
        ylim = [-30, 30]

    # Crop again to the plot area and set limits
    extractor.crop_to_plot_area()
    extractor.set_limits(xlim, ylim)

    # Run the full data extraction process
    extractor.process()
    # print("Data points:", extractor.data_points)
    # extractor.remove_outliers()

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(csv_folder, exist_ok=True)

    # Plot intermediate results
    if args.debug:
      extractor.plot_thresholded_image()
      extractor.plot_cleaned_image()
      extractor.plot_contours()

    # Plot final data points and median line
    # filename = "extracted_rcs.png"
    filename = os.path.basename(image_path)
    figure_path = os.path.join(output_folder, f"extracted-{filename}")

    data_points = extractor.data_points
    median = calculate_median_rcs(data_points)

    if data_points is not None and len(data_points):
      # Define plot settings
      settings = {
          "title": "Extracted Plot: " + filename,
          "x_label": "Aspect Angle (deg)",
          "y_label": "RCS (dBsm)",
          "type": "SAMPLE",
          "x_lim": xlim,
          "y_lim": ylim
      }

      # Generate the sample figure
      ax = generate_sample_figure(settings)

      ax.plot(data_points[:, 0], data_points[:, 1], linestyle='-', color='blue', linewidth=0.8)

      plot_median(median, data_points)

      plt.savefig(figure_path, dpi=300)

      plt.close()
      # print("\nData extraction and visualization complete!\n")
    else:
        print("\n!!!!! ERROR EXTRACTING DATA !!!!!\n")

        
    

    
    name = os.path.splitext(filename)[0]
    csv_path = os.path.join(csv_folder, name + ".csv")
    save_to_csv(data_points, csv_path)

    result = {
        "origin": origin,
        "xlim": xlim,
        "ylim": ylim,
        "median_rcs": median,
        "data_points": data_points,
        "csv_path": csv_path,
        "figure_path": figure_path
    }
    

    if debug:
        print("Data points:", data_points)
        print("Median:", median)

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run plot extraction with command line settings.")
    parser.add_argument("--image_path", type=str, default="input/sample.png", help="Path to the input image.")
    parser.add_argument("--target_color", type=str, default="blue", help="Target color to filter (e.g., '#034730' or 'blue').")
    parser.add_argument("--delta", type=int, default=20, help="Delta value for color extraction.")
    parser.add_argument("--kernel_size", type=int, default=1, help="Kernel size for morphological cleaning.")
    parser.add_argument("--thin", type=int, default=2, help="Thin factor used when finding contours.")
    parser.add_argument("--output", type=str, default="output", help="Save outputs to this folder.")
    parser.add_argument("--debug", action="store_true", help="Activate debug mode to visualize steps.")
    args = parser.parse_args()
    main(args)
    # python run_extraction.py --image_path input/alpha-stim.png --target_color "#034730" --delta 20 --kernel_size 1 --thin 2 --debug