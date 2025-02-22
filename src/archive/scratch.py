import cv2
from utils import detect_rotation, rotate_image

# Read the image
# input_file = 'input/sample_sine_wave.png'
input_file = 'crooked.png'
image = cv2.imread(input_file)
if image is None:
    raise ValueError("Could not read image. Check the file path.")

# Detect rotation angle
angle = detect_rotation(image, debug=False)
print(f"Detected angle: {angle:.2f} degrees")

# Rotate image if angle is significant
if abs(angle) > 0.0:
    rotated = rotate_image(image, angle)
    # Save the rotated image
    cv2.imwrite('rotated.png', rotated)
    print(f"Rotated image saved (correction angle: {angle:.2f})")
else:
    print("No significant rotation detected")