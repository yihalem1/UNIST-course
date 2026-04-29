import numpy as np
import cv2
from matchPics import matchPics
from scipy.ndimage import rotate
import matplotlib.pyplot as plt
from helper import plotMatches

cv_cover = cv2.imread('../data/cv_cover.jpg')

# There are 36 increments: 0, 10, 20, ..., 350 (i.e., 36 increments of 10 degrees)
histogram = np.zeros(36)

for i in range(36):
    # Rotate image: i*10 gives the current angle in degrees
    angle = i * 10
    rotate_cover = rotate(cv_cover, angle)
    # Compute features, descriptors and match features
    matches, locs1, locs2 = matchPics(cv_cover, rotate_cover)

    # display and save matched features at specific angles: 10, 70, and 190 degrees.
    if angle in [10, 70, 190]:
        plotMatches(cv_cover, rotate_cover, matches, locs1, locs2)
    # Update histogram with the number of matching keypoints
    histogram[i] = len(matches)

# Prepare corresponding degree labels for the x-axis
degrees = np.arange(0, 360, 10)

# Display
plt.figure()
plt.bar(degrees, histogram, width=8, color='green')  # Adjusted width for visual clarity
plt.xlabel('Degrees)')
plt.ylabel('Matching Keypoints')
plt.title('BRIEF and Rotations')
plt.show()
