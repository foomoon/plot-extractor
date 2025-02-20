import os
import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Use a non-GUI backend
import matplotlib.pyplot as plt
from find_plot_corners import find_plot_corners
from utils import filter_colors

class GraphDataExtractor:
    def __init__(self, image_name=None):
        if image_name is not None:
            self.image = self.load_image(image_name)
        else:
            self.image = None
        self.kernel_size = 3
        self.x_min = 0
        self.x_max = 180
        self.y_min = -30
        self.y_max = 30
        self.thresholded_image = None
        self.cleaned_image = None
        self.subtracted_image = None
        self.data_points = None
        self.contours = None
        self.thin_factor = 1
    
    def set_thin(self, thin):
        self.thin_factor = thin

    def set_limits(self, xlim, ylim):
        self.x_min, self.x_max = xlim
        self.y_min, self.y_max = ylim

    def set_kernel_size(self, kernel_size):
        self.kernel_size = kernel_size

    def load_image(self, image_path, target_color='blue', delta=20):
        """Loads the image in grayscale."""
        # image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        image = cv2.imread(image_path)
        # image = filter_colors(image, target_color=target_color, delta=delta) # filter only black colors
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.image = image
        return image
    
    def filter_to_gray(self, target_color='blue', delta=20):
        image = self.image
        if len(image.shape) > 2:
            image = filter_colors(image, target_color=target_color, delta=delta) # filter only black colors
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.image = image
        else:
            print("WARNING: Image already gray scale, cannot convert")
        return image
    
    def get_image(self):
        return self.image

    def threshold_image(self):
        """Thresholds the image to binary (invert if needed)."""
        _, thresholded = cv2.threshold(self.image, 127, 127, cv2.THRESH_BINARY_INV)
        self.thresholded_image = thresholded
        return thresholded
    
    def clean_image(self):
        """Applies morphological operations to clean the image."""
        iter = 1
        kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
        cleaned = cv2.morphologyEx(self.thresholded_image, cv2.MORPH_OPEN, kernel, iterations=iter)
        # Mask the outer 10 pixels from each edge
        H, W = self.image.shape[:2]
        border_width = int(0.02 * H)
        cleaned[:border_width, :] = 0
        cleaned[-border_width:, :] = 0
        cleaned[:, :border_width] = 0
        cleaned[:, -border_width:] = 0
        self.cleaned_image = cleaned
        return cleaned

    def find_contours(self):
        """Finds and extracts contours from the cleaned image."""
        k = self.thin_factor
        kernel = np.ones((k, k), np.uint8)
        self.eroded_image = cv2.erode(self.cleaned_image, kernel, iterations=1)
        contours, _ = cv2.findContours(self.eroded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.contours = contours
        return contours

    def extract_data_points(self):
        """Extracts the data points from contours and scales them."""
        contours = self.contours
        data_points = []

        contour_count = len(contours)
        # print(f"Found {contour_count} contour(s)\n")

        if contour_count == 0:
            print('Exiting contour extraction')
            return data_points

        for contour in contours:
            epsilon = 0.0001 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            for point in approx:
                x, y = point[0]
                data_points.append((x, y))

        data_points = np.array(data_points)
        data_points = self.sort_data_points(data_points)
        data_points = self.scale_data_points(data_points)
        self.data_points = data_points
        return data_points
    
    def sort_data_points(self, data_points):
        """Sort points"""
        # data_points = data_points[data_points[:, 0].argsort()]
        data_points = self.sort_data_points_custom(data_points)
        return data_points
    
    def sort_data_points_custom(self, data_points):
        """
        Custom sort of data points.
        
        Primary sort is by x value in ascending order.
        For groups of points with the same x value, the points are ordered
        such that the first point in the group is the one whose y value is
        closest to the last y value from the previously sorted group,
        and the rest are ordered greedily based on proximity.
        """
        # Convert to a list of tuples for easier processing
        points = [tuple(pt) for pt in data_points]
        # First, sort by x (primary key)
        points.sort(key=lambda p: p[0])
        
        from itertools import groupby
        # Group by x value (since points are sorted by x, groupby works as expected)
        groups = []
        for x_val, group in groupby(points, key=lambda p: p[0]):
            groups.append((x_val, list(group)))
        
        sorted_points = []
        for i, (x_val, group) in enumerate(groups):
            if i == 0:
                # For the first group, simply sort by y ascending
                group_sorted = sorted(group, key=lambda p: p[1])
                sorted_points.extend(group_sorted)
            else:
                # For subsequent groups, start with the point in the group whose y is
                # closest to the last sorted point's y value, and then order the rest greedily.
                current_order = []
                last_y = sorted_points[-1][1]
                group_remaining = group.copy()
                while group_remaining:
                    # Choose the point minimizing the absolute difference in y with last_y.
                    next_point = min(group_remaining, key=lambda p: abs(p[1] - last_y))
                    current_order.append(next_point)
                    last_y = next_point[1]
                    group_remaining.remove(next_point)

                # only include first and last point since intermediate points are on a vertical line
                # there are not needed
                if (len(current_order) > 1):
                    current_order = [current_order[0], current_order[-1]] 
                sorted_points.extend(current_order)
        
        return np.array(sorted_points, dtype=data_points.dtype)
    
    def scale_data_points(self, data_points):
        """Scales data points to fit the user-defined limits based on image dimensions."""
        # Assuming the minimum values are always zero
        width = self.image.shape[1]  # Width of the image
        height = self.image.shape[0]  # Height of the image

        # Assuming the minimum values are always zero
        x_min, x_max = width, 0
        y_min, y_max = height, 0

        # Convert data_points to float to avoid integer rounding issues
        data_points = data_points.astype(np.float128)

        # print(f"Origin: {self.x_min} , {self.y_min}")
        # Scale x values
        data_points[:, 0] = 0*self.x_min + ((data_points[:, 0] - x_min) / (x_max - x_min)) * (self.x_max - self.x_min)
        # Scale y values
        data_points[:, 1] = self.y_min + ((data_points[:, 1] - y_min) / (y_max - y_min)) * (self.y_max - self.y_min)

        # flip x left to right
        data_points[:, 0] = self.x_max - data_points[:, 0]
        return data_points
    
    def remove_outliers(self, threshold=1.5):
        """Removes outliers from the data_points using the Interquartile Range (IQR) method."""
        if self.data_points.size == 0:
            print("Data points are empty. Please extract data first.")
            return
        
        # Convert data_points to a numpy array for easier manipulation
        data_array = np.array(self.data_points)
        # original_length = len(data_array)
        
        # Calculate the first (Q1) and third (Q3) quartiles
        Q1 = np.percentile(data_array, 25, axis=0)
        Q3 = np.percentile(data_array, 75, axis=0)
        IQR = Q3 - Q1
        
        # Define the lower and upper bounds for outliers
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        # Filter the data to exclude outliers
        mask = np.all((data_array >= lower_bound) & (data_array <= upper_bound), axis=1)
        self.data_points = np.array(data_array[mask].tolist())

        # print(f"Removed outliers. Kept: {len(self.data_points)} of {original_length}\n")
 
    def find_corners(self, debug: bool = False):
        origin, top_right = find_plot_corners(self.image, debug=debug)
        return origin, top_right
    
    def crop(self, origin, top_right):
        # Unpack the corner coordinates
        x_origin, y_origin = origin
        x_top_right, y_top_right = top_right
        
        # For robustness, determine min/max for x and y
        x_left = min(x_origin, x_top_right)
        x_right = max(x_origin, x_top_right)
        y_top = min(y_origin, y_top_right)   # Smaller y value (closer to the top)
        y_bottom = max(y_origin, y_top_right)  # Larger y value (closer to the bottom)
        
        # Given our assumptions, typically:
        cropped = self.image[y_top:y_bottom, x_left:x_right]
        self.image = cropped
        return cropped
    
    def crop_to_plot_area(self, iterations=1, margin=4):
        """Crops the image to the plot area."""
        for i in range(iterations):
            # print(f"\nCrop, iteration: {i + 1}")
            origin, top_right = self.find_corners()
            origin = (origin[0] + margin, origin[1] - margin)
            top_right = (top_right[0] - margin, top_right[1] + margin)
            # print(f"Origin: {origin}")
            # print(f"Top Right: {top_right}")
            self.crop(origin, top_right)
        # print("\nPlot cropping complete!\n")

    def get_image_area(self):
        """Returns the area of the image in pixels."""
        height, width = self.image.shape[:2]
        return width * height

    def process(self):
        """Runs the entire data extraction process."""
        self.threshold_image()
        self.clean_image()
        self.find_contours()
        self.extract_data_points()

    def plot_image(self, image, file_path):
        """Plots the thresholded image."""
        plt.figure(figsize=(6, 6))
        plt.imshow(image, cmap='gray')
        plt.title('Thresholded Image Before Morphology')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

    def plot_thresholded_image(self, filename="output/threshold_output.png"):
        """Plots the thresholded image."""
        self.plot_image(self.thresholded_image, filename)

    def plot_cleaned_image(self, filename="output/cleaned_output.png"):
        """Plots the cleaned image."""
        self.plot_image(self.cleaned_image, filename)

    def plot_contours(self, file_path="output/contour_output.png"):
        """Draws contours on a blank image."""
        contours = self.contours
        contour_image = np.zeros_like(self.image)  # Same size as the original image, filled with black (0)
        cv2.drawContours(contour_image, contours, -1, (255), 2)  # (-1) draws all contours
        cv2.imwrite(file_path, contour_image)  # Save contour image
