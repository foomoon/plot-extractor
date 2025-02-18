import cv2
import numpy as np
from PIL import ImageColor
from math import degrees


def calculate_median_rcs(data):
    """
    Calculates the median Radar Cross Section (RCS) in dBsm from a NumPy array.
    
    Parameters:
        data (np.ndarray): A 2D NumPy array where:
            - Column 0: Aspect angles (x-values)
            - Column 1: RCS values in dBsm (y-values)
    
    Returns:
        float: The median RCS in dBsm.
    """
    if data.shape[1] != 2:
        raise ValueError("Input array must have exactly two columns (aspect angles, RCS values).")

    # Extract RCS values (y-values) from the second column
    rcs_values_dbsm = data[:, 1]

    # Convert dBsm values to linear scale
    rcs_linear = 10 ** (rcs_values_dbsm / 10)

    # Compute median in linear scale
    median_rcs_linear = np.median(rcs_linear)

    # Convert back to dBsm
    median_rcs_dbsm = 10 * np.log10(median_rcs_linear)
    
    return median_rcs_dbsm



def string_to_hsv(color_str: str) -> np.ndarray:
    """
    Convert a color string (e.g., "red", "#FF0000", "navy") to an HSV numpy array using OpenCV.
    
    The returned HSV values are in OpenCV's scale:
      - Hue: 0-180 (np.uint8)
      - Saturation: 0-255 (np.uint8)
      - Value: 0-255 (np.uint8)
    
    Parameters:
        color_str (str): The input color string.
        
    Returns:
        np.ndarray: A numpy array with shape (3,) containing (h, s, v).
    """
    # Convert the color string to an RGB tuple (values in the range 0-255)
    rgb = ImageColor.getrgb(color_str)
    
    # Create a 1x1 pixel image with this color (in RGB order)
    rgb_pixel = np.uint8([[list(rgb)]])
    
    # Convert the 1x1 RGB image to HSV using OpenCV.
    hsv_pixel = cv2.cvtColor(rgb_pixel, cv2.COLOR_RGB2HSV)
    
    # Return the HSV values as a numpy array (no int cast)
    return hsv_pixel[0, 0]




def filter_colors(image, target_color: str = 'black', delta: int = 20) -> np.ndarray:
    """
    Extracts regions of an image that are black, green, white, or blue,
    and returns an image where the preserved areas maintain their original colors,
    while non-preserved areas are filled with white.
    
    Parameters:
        image_path (str): The file path to the image.
        
    Returns:
        result (np.ndarray): The processed image with non-preserved areas filled with white.
    """
    # Load the image
    
    if image is None:
        raise ValueError("Image not found. Check the provided path.")
    
    # Convert the image from BGR to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define HSV range for black (low brightness in the V channel).
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    mask_black = cv2.inRange(hsv, lower_black, upper_black)
    
    # Define HSV range for white.
    # White typically has low saturation and high value.
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    # Compute target color from string
    target = string_to_hsv(target_color)
    target_hue = target[0]
    # delta = 20
    lower_target = np.array([max(target_hue-delta,0), 150, 0]) # from partial saturation and no brightness
    upper_target = np.array([min(target_hue + delta,180), 255, 255]) # to full saturation and full brightness
    mask_target = cv2.inRange(hsv, lower_target, upper_target)
    
    # Combine all masks using bitwise OR operations.
    combined_mask = mask_black
    # combined_mask = cv2.bitwise_or(combined_mask, mask_black)
    combined_mask = cv2.bitwise_or(combined_mask, mask_white)
    combined_mask = cv2.bitwise_or(combined_mask, mask_target)
    # combined_mask = cv2.bitwise_or(mask_white, mask_target)

    
    # Create a white background image of the same size as the original image.
    white_bg = np.full_like(image, 255)  # 255 for white in BGR
    
    # Create the output image by copying the white background.
    # Then, for all pixels where the mask is 255 (preserved colors), copy the original pixel.
    result = white_bg.copy()
    result[combined_mask == 255] = image[combined_mask == 255]
    
    return result



def detect_rotation(image, debug=False):
    """
    Detect the rotation angle of a plot image using Hough transform.
    
    Parameters:
        image: Input image (grayscale or BGR)
        debug: If True, save intermediate processing steps
        
    Returns:
        angle: Rotation angle in degrees (positive = counterclockwise)
    """
    # Convert to grayscale if needed
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    if debug:
        cv2.imwrite("output/edges.png", edges)
    
    # Detect lines using Hough transform
    lines = cv2.HoughLinesP(edges, 1, np.pi/180/10, 
                           threshold=100, 
                           minLineLength=200, 
                           maxLineGap=50)
    
    if lines is None:
        return 0
    
    lines = np.squeeze(lines)

    angles = []
    lengths = []
    for line in lines:
        x1, y1, x2, y2 = line
        # Calculate line length
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Calculate angle of the line
        if x2 - x1 != 0:  # Avoid division by zero
            angle = degrees(np.arctan2(y2 - y1, x2 - x1))
            # Normalize angles to -45 to 45 degrees range
            if angle > 45:
                angle -= 90
            elif angle < -45:
                angle += 90
            angles.append(angle)
            lengths.append(length)

        if debug:
            print(line, int(length), angle)
    
    if not angles:
        return 0
    
    # Use weighted median based on line lengths
    sorted_pairs = sorted(zip(angles, lengths), key=lambda x: -x[1])
    total_length = sum(lengths)
    cumulative_length = 0
    for angle, length in sorted_pairs:
        cumulative_length += length
        if cumulative_length >= total_length/2:
            rotation_angle = angle
            break
    
    if debug:
        # Draw detected lines with thickness proportional to length
        debug_img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        for line, length in zip(lines, lengths):
            x1, y1, x2, y2 = line
            # thickness = int(max(1, length/100))  # Scale thickness based on length
            cv2.line(debug_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.circle(debug_img, (x1, y1), 10, (0, 255, 0), 2)
            cv2.circle(debug_img, (x2, y2), 10, (255, 255, 0), 2)
        cv2.imwrite("output/detected_lines.png", debug_img)
        print(f"Found {len(angles)} lines")
        print(f"Line lengths: min={min(lengths):.1f}, max={max(lengths):.1f}, mean={np.mean(lengths):.1f}")
        print(f"Detected rotation angle: {rotation_angle:.2f} degrees")
    
    return rotation_angle

def rotate_image(image, angle, center=None):
    """
    Rotate an image by a given angle around its center.
    
    Parameters:
        image: Input image
        angle: Rotation angle in degrees (positive = counterclockwise)
        center: Point to rotate around (if None, use image center)
    
    Returns:
        Rotated image
    """
    height, width = image.shape[:2]
    if center is None:
        center = (width // 2, height // 2)
    
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale=1.0)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height),
                                  flags=cv2.INTER_LINEAR)
    
    return rotated_image
