import cv2
import numpy as np

# Load damaged photo
img = cv2.imread('/app/inputs/old_w_scratch/a.png', cv2.IMREAD_COLOR)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Step 1: Edge detection
edges = cv2.Canny(gray, threshold1=50, threshold2=150)

# Step 2: Morphological operations to make edges thicker
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
mask = cv2.dilate(edges, kernel, iterations=1)

# Step 3: Optional - thresholding for very bright spots
_, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)  # very bright = possible scratch
mask = cv2.bitwise_or(mask, thresh)

# Invert (if needed: white = scratch, black = background)
#mask = cv2.bitwise_not(mask)

# Save mask
cv2.imwrite('/app/outputs/mask/mask.png', mask)

print("Mask saved as mask.png")


# SAM should be used.