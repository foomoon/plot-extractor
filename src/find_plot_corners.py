import os
import cv2
import numpy as np

def find_plot_corners(image, debug=False, output_folder="output"):
    """
    Attempts to locate both the origin (bottom-left) and the top-right corner of a plot.
    
    Assumptions:
      - The plot is drawn on a light background with dark grid/axis lines.
      - Thick lines (extracted via morphological operations) are assumed to be the plot boundaries or axes.
      - The origin is near the bottom-left and the top-right corner lies above and to the right of it.
    
    Parameters:
      image: Input image (BGR).
      debug: If True, shows intermediate images and prints debug info.
    
    Returns:
      (origin, top_right): Tuple of pixel coordinates for the origin and top-right corner.
                            If detection fails, one or both may be None.
    """
   
    # Convert image to grayscale and invert it so dark lines become white
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image
    # gray = image
    inv_gray = cv2.bitwise_not(gray)
    
    # Threshold the image to obtain a binary image (lines in white)
    _, binary = cv2.threshold(inv_gray, 50, 255, cv2.THRESH_BINARY)
    if debug:
        cv2.imwrite(os.path.join(output_folder, "binary.png"), binary)  # Save contour image
        
    # Use morphological operations to extract thick vertical lines.
    # The kernel size is based on the image dimensions; adjust as necessary.
    vert_kernel_len = max(3, image.shape[0] // 40)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vert_kernel_len))
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    # Extend vertical lines using closing with a tall kernel
    extend_vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, image.shape[0] // 5))
    vertical_lines = cv2.morphologyEx(vertical_lines, cv2.MORPH_CLOSE, extend_vert_kernel, iterations=2)
    if debug:
        cv2.imwrite(os.path.join(output_folder, "vertical_lines.png"), vertical_lines)  # Save contour image

    # Use morphological operations to extract thick horizontal lines.
    hor_kernel_len = max(3, image.shape[1] // 40)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (hor_kernel_len, 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    # Extend horizontal lines using closing with a wider kernel
    extend_hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (image.shape[1] // 5, 1))
    horizontal_lines = cv2.morphologyEx(horizontal_lines, cv2.MORPH_CLOSE, extend_hor_kernel, iterations=2)
    if debug:
        cv2.imwrite(os.path.join(output_folder, "horizontal_lines.png"), horizontal_lines)  # Save contour image
    
    # Find intersections between the vertical and horizontal thick lines.
    intersections = cv2.bitwise_and(vertical_lines, horizontal_lines)
    
    # Cleanup border (a little janky but doesn't hurt)
    border_width = 15
    intersections[:border_width, :] = 0
    intersections[-border_width:, :] = 0
    intersections[:, :border_width] = 0
    intersections[:, -border_width:] = 0
    
    if debug:
        cv2.imwrite(os.path.join(output_folder, "intersections.png"), intersections)  # Save contour image
    
    # Find contours in the intersections mask to get candidate intersection points.
    contours, _ = cv2.findContours(intersections, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        if debug:
            print("No intersections found.")
        return None, None
    
    if debug:
        contour_image = np.zeros_like(gray)  # Same size as the original image, filled with black (0)
        cv2.drawContours(contour_image, contours, -1, (255), 2)  # (-1) draws all contours
        cv2.imwrite(os.path.join(output_folder, "corner_contours.png"), contour_image)  # Save contour image

    
    # Compute candidate points (use the center of each contour's bounding rectangle)
    candidate_points = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # candidate_points.append((x + w // 2, y + h // 2))
        candidate_points.append((x,y))
    
    if debug:
        print(f"{len(candidate_points)} Candidate intersections:", candidate_points)
    
    # Heuristic for the origin (bottom-left):
    # Choose the point with the smallest x and largest y.

    # Seems to be working better:
    origin = sorted(candidate_points, key=lambda pt: (-pt[1], pt[0]))[0]

    # Find the top-right point do opposite
    top_right = sorted(candidate_points, key=lambda pt: (pt[1], -pt[0]))[0]
    
   
    
    if debug:
        # Create a copy of the image to mark candidate points and the chosen corners.
        debug_img = image.copy()
        
        # Mark the origin in red.
        if origin:
            cv2.circle(debug_img, origin, 20, (0, 0, 255), -1)
        # Mark the top-right corner in green.
        if top_right:
            cv2.circle(debug_img, top_right, 20, (0, 255, 0), -1)

        # Mark all candidate intersections in purple.
        for pt in candidate_points:
            cv2.circle(debug_img, pt, 8, (255, 0, 255), -1)

        cv2.imwrite(os.path.join("output", "corners.png"), debug_img)  # Save contour image


    
    return origin, top_right

# Example usage:
if __name__ == '__main__':
    img = cv2.imread('example_plot.png')
    origin, top_right = find_plot_corners(img, debug=True)
    
    if origin:
        print("Origin (bottom-left) found at:", origin)
    else:
        print("Origin not found.")
    
    if top_right:
        print("Top-right corner found at:", top_right)
    else:
        print("Top-right corner not found.")
