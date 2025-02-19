import os
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

    # Figure properties
    classification = getattr(args, 'classification', "SAMPLE")
    dpi            = getattr(args, "dpi", 300)
    


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
    origin, _ = extractor.find_corners(debug=debug)

    # Find plot corners (origin) and extract axes labels
    if xlim is None or ylim is None:
        print("No axes specified, attempting to extract from image")
        image = extractor.get_image()
        x_axis, y_axis = extract_axes_labels(image, origin, DEBUG=args.debug, factor=0.004)
        
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

    # Convert to grayscale after isolating target color
    extractor.filter_to_gray(target_color, delta=delta)
    # Crop again to the plot area
    extractor.crop_to_plot_area()
    # Set limits
    extractor.set_limits(xlim, ylim)
    # Run the full data extraction process
    extractor.process()
    # 
    data_points = extractor.data_points
    median = calculate_median_rcs(data_points)

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
      # Create output folder if it doesn't exist
      os.makedirs(output_folder, exist_ok=True)
      figure_path = os.path.join(output_folder, "extracted-image.png")
      ax = generate_sample_figure(settings)
      ax.plot(data_points[:, 0], data_points[:, 1], linestyle='-', color='blue', linewidth=0.8)
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