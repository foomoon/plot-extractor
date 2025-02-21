import re
import cv2
import pytesseract
import statistics
import matplotlib
matplotlib.use("Agg")  # Use a non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import math

def extract_axes_labels(img_input, lower_left, factor=0.004, DEBUG=False, debug_file_path="output/axes-extraction.png"):

    if len(img_input.shape) > 2:
        img = cv2.cvtColor(img_input, cv2.COLOR_RGB2GRAY)
    else:
        img = img_input


    # Enhance contrast using histogram equalization
    # equalized = cv2.equalizeHist(img)
    # # Further enhance text using adaptive thresholding
    # img = cv2.adaptiveThreshold(equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    #                               cv2.THRESH_BINARY, 11, 2)

    bottom, right = img.shape[:2]

    m = int(bottom * factor)
    margin = (m,m)

    n = 1 # values should range between (0 and 1)
    # smaller values will produce larger roi

    # Define ROIs based on lower_left and margins
    y_roi_right, x_roi_top = lower_left
    x_roi_top = x_roi_top + margin[1]
    y_roi_right = y_roi_right - margin[0]
    
    y_roi_left = int(y_roi_right / (1 + n))
    x_roi_bottom = x_roi_top + int((bottom - x_roi_top) / (1 + n))
    
    x_axis_region = img[x_roi_top:x_roi_bottom, 0:right]
    y_axis_region = img[0:bottom, y_roi_left:y_roi_right]

    useOpenCV = True

    if DEBUG and not useOpenCV:
        plt.figure(figsize=(6, 6))
        plt.imshow(img, cmap='gray')
        circle = patches.Circle(lower_left, radius=5, edgecolor='red', facecolor='none', linewidth=2)
        plt.gca().add_patch(circle)
        x_roi_rect = patches.Rectangle((0, x_roi_top), right, x_roi_bottom-x_roi_top, edgecolor='red', facecolor='none', linewidth=1)
        y_roi_rect = patches.Rectangle((y_roi_left, 0), y_roi_right-y_roi_left, bottom, edgecolor='red', facecolor='none', linewidth=1)
        plt.gca().add_patch(x_roi_rect)
        plt.gca().add_patch(y_roi_rect)
        plt.tight_layout()
        plt.savefig(debug_file_path)
        plt.close()

    

    if DEBUG and useOpenCV:
        # If the image is grayscale (2D array), convert it to BGR so that color drawing works.
        if len(img.shape) == 2:
            img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            img_color = img.copy()
        # Draw the circle:
        cv2.circle(img_color, lower_left, 20, (0, 255, 0), thickness=3)
        # Draw the x-axis region of interest (ROI) rectangle:
        cv2.rectangle(img_color, (0, x_roi_top), (right, x_roi_bottom), (0, 0, 255), thickness=3)
        # Draw the y-axis region of interest (ROI) rectangle:
        cv2.rectangle(img_color, (y_roi_left, 0), (y_roi_right, bottom), (0, 0, 255), thickness=3)
        # Save the final image
        cv2.imwrite(debug_file_path, img_color)

    def preprocess_for_ocr(cropped):
        _, thresh = cv2.threshold(cropped, 150, 255, cv2.THRESH_BINARY)
        return thresh

    y_axis_preprocessed = preprocess_for_ocr(y_axis_region)
    x_axis_preprocessed = preprocess_for_ocr(x_axis_region)

    # Use pytesseract to extract text from the cropped regions
    y_axis_text = pytesseract.image_to_string(y_axis_preprocessed, config=r'--psm 6')
    x_axis_text = pytesseract.image_to_string(x_axis_preprocessed, config=r'--psm 7')

    


    def extract_numbers(text):
        """
        Extracts all numbers (including negatives and decimals) from a text string.
        """
        text = text.replace("O", "0").replace("_","-").replace("$","3").replace("- ","-").replace("~","-")
        # Replace 'L' with '1' if it is preceded or followed by a digit.
        text = re.sub(r'(?<=\d)L|L(?=\d)', '1', text)
        pattern = r'[‐–—-]?\d+(?:\.\d+)?'
        matches = re.findall(pattern, text)
        return [float(num.replace("—", "-").replace("–", "-").replace("‐", "-")) for num in matches]
  
    # Get OCR numbers; note that we reverse y-axis values since OCR order might be flipped
    y_axis_values = extract_numbers(y_axis_text)
    x_axis_values = extract_numbers(x_axis_text)
    y_axis_values = y_axis_values[::-1]

    if DEBUG:
        print("X-axis Text:", x_axis_text)
        print("Extracted X-axis:", x_axis_values)
        print("Y-axis Text:", y_axis_text)
        print("Extracted Y-axis:", y_axis_values)


    # ----- Sanity Check Helpers -----
    def is_monotonic(values):
        """Check if values are strictly non-decreasing or non-increasing."""
        return all(x <= y for x, y in zip(values, values[1:])) or all(x >= y for x, y in zip(values, values[1:]))

    def compute_most_common_delta(diffs, round_digits=2):
        """Compute the most common difference using statistics.mode.
           If no unique mode exists, fall back to the median."""
        rounded_diffs = [round(diff, round_digits) for diff in diffs]
        try:
            # statistics.mode returns the most common value
            return statistics.mode(rounded_diffs)
        except statistics.StatisticsError:
            # No unique mode; fall back to using the median
            return statistics.median(rounded_diffs)

    def sanitize_axis_values(values, tol=0.1):
        """
        Sanitize axis numbers by ensuring spacing is consistent.
        Uses the most common delta (step size) as the expected value.
        If a gap is found which is a multiple of expected_delta, fill in missing numbers.
        If a delta is significantly different, replace it with the expected increment.
        """
        if len(values) < 2:
            return values
            
        # Determine monotonicity (increasing or decreasing)
        increasing = values[1] >= values[0]
        # Compute absolute differences between consecutive numbers
        diffs = [abs(b - a) for a, b in zip(values, values[1:])]
        expected_delta = compute_most_common_delta(diffs)
        print(f"  Expected Delta: {expected_delta}    {diffs}")
        corrected = [values[0]]
        for idx in range(len(values)-1):
            actual_diff = values[idx+1] - values[idx]
            abs_diff = abs(actual_diff)
            direction = 1 if increasing else -1
            # If actual difference is close enough to expected_delta, accept the value
            if math.isclose(abs_diff, expected_delta, rel_tol=tol):
                corrected.append(values[idx+1])
            else:
                # Delta doesn't match expectations; substitute with expected increment.
                corrected.append(corrected[-1] + direction * expected_delta)
        return corrected

    # Check monotonicity and warn if needed.
    if not is_monotonic(x_axis_values):
      print("Warning: extracted x_axis_values are not monotonic. ")
      print(x_axis_values)
    if not is_monotonic(y_axis_values):
      print("Warning: extracted y_axis_values are not monotonic. ")
      print(y_axis_values)

    #   y_axis_values = sanitize_axis_values(y_axis_values)

    return x_axis_values, y_axis_values

# Main execution for testing purposes
if __name__ == "__main__":
    img = cv2.imread('sine_plot.png', cv2.IMREAD_GRAYSCALE)
    lower_left = (100, 400)  # Adjust as needed
    x_axis, y_axis = extract_axes_labels(img, lower_left)
    print("X-Axis:", x_axis)
    print("Y-Axis:", y_axis)