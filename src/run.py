import os
import cv2
import matplotlib
matplotlib.use("Agg")  # Use a non-GUI backend
import matplotlib.pyplot as plt
from graph_data_extractor import GraphDataExtractor
from extract_axes import extract_axes_labels
from utils import calculate_median_rcs

from sample_figure import generate_sample_figure, plot_median


def validate_limits(xlim):
  """Validates the x and y limits."""
  if xlim[0] >= xlim[1]:
      print(f"Invalid axis limits: {xlim}")
      return False
  if xlim[1] - xlim[0] < 1:
      print(f"Invalid axis limits: {xlim}")
      return False
  return True

def main(image, args):
    # Settings and paths from arguments

    # Analysis properties
    target_color = getattr(args, 'target_color', 'blue')
    delta        = getattr(args, 'delta', 20)
    debug        = getattr(args, 'debug', False)
    output_folder= getattr(args, 'output_folder', 'static/images')
    thin         = getattr(args, 'thin', 6)
    kernel_size  = getattr(args, 'kernel_size', 1)
    xlim         = getattr(args, "x_lim", None)
    ylim         = getattr(args, "y_lim", None)
    title        = getattr(args, "title", "Title")
    x_label      = getattr(args, "x_label", "X Axis")
    y_label      = getattr(args, "y_label", "Y Axis")
    isMedian     = getattr(args, "isMedian", False)
    axes_extract_factor = 0.004

    # Figure properties
    classification = getattr(args, 'classification', "SAMPLE")
    dpi            = getattr(args, "dpi", 300)

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    if debug:
        print("DEBUG MODE: ")

    # Initialize extractor and load image
    extractor = GraphDataExtractor()
    extractor.image = image.copy()
    extractor.set_kernel_size(kernel_size)
    extractor.set_thin(thin)

    # Get original area and crop if necessary
    original_image_area = extractor.get_image_area()
    extractor.crop_to_plot_area()
    min_plot_area = original_image_area * 0.8
    plot_area = extractor.get_image_area()
    
    if plot_area < min_plot_area:
        # extractor.load_image(image_path, target_color=target_color, delta=delta)
        extractor.image = image
        print(f"Reloaded image area = {extractor.get_image_area()}\n")

    # Get plot area origin first
    origin, _ = extractor.find_corners(debug=debug, output_folder=output_folder)

    axes_file_path = os.path.join(output_folder, "axes-extraction.png")

    # Find plot corners (origin) and extract axes labels
    if xlim is None or ylim is None:
        print("No axes specified, attempting to extract from image")
        image = extractor.get_image()
        
        x_axis, y_axis = extract_axes_labels(image, origin, DEBUG=args.debug, factor=axes_extract_factor, debug_file_path=axes_file_path)
        
        if not x_axis:
            print("No x axis found, using default")
            x_axis = [0, 180]
        if not y_axis:
            print("No y axis found, using default")
            y_axis = [-30, 30]

        xlim = [x_axis[0], x_axis[-1]]
        ylim = [y_axis[0], y_axis[-1]]

        if not validate_limits(xlim):
            print("Using default x limits")
            xlim = [0, 180]
        if not validate_limits(ylim):
            print("Using default y limits")
            ylim = [-30, 30]
    else:
        # save a blank image
        print(f"Manual Axes input... overwriting {axes_file_path}")
        cv2.imwrite(axes_file_path, image)

    # Convert to grayscale after isolating target color
    extractor.filter_to_gray(target_color, delta=delta)
    # Crop again to the plot area
    extractor.crop_to_plot_area()
    # Set limits
    extractor.set_limits(xlim, ylim)
    # Run the full data extraction process
    extractor.process()

    if debug:
        extractor.plot_thresholded_image(os.path.join(output_folder, "extract-threshold.png"))
        extractor.plot_cleaned_image(os.path.join(output_folder, "extract-cleaned.png"))
        extractor.plot_contours(os.path.join(output_folder, "extract-contours.png"))


    # Get data
    data_points = extractor.data_points
    median = None

    if data_points is not None and len(data_points):
        # Define plot settings
        settings = {
            "title": title,
            "x_label": x_label,
            "y_label": y_label,
            "type": classification,
            "x_lim": xlim,
            "y_lim": ylim
        }

        # Generate the sample figure
        figure_path = os.path.join(output_folder, "extracted-image.png")
        ax = generate_sample_figure(settings)
        ax.plot(data_points[:, 0], data_points[:, 1], linestyle='-', color='blue', linewidth=0.8)
        print(f"Saving figure to {figure_path}")

        if isMedian:
            median = calculate_median_rcs(data_points)
            print(f"Plotting Median RCS: {median}")
            plot_median(median, data_points)
            

        plt.savefig(figure_path, dpi=dpi)
        plt.close()

        
    else:
        print("\n!!!!! ERROR EXTRACTING DATA !!!!!\n")
        


    result = {
        "origin": origin,
        "xlim": xlim,
        "ylim": ylim,
        "median_rcs": median,
        "data_points": data_points,
        "extracted_image": figure_path
    }
    

    if debug:
        print("Data points:", data_points)
        print("Median:", median)

    return result