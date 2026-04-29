import numpy as np
import cv2
from matchPics import matchPics
from helper import plotMatches
import matplotlib.pyplot as plt

# Read the original image (in color)
cv_cover = cv2.imread('../data/cv_cover.jpg')

# Convert original image to grayscale for noise generation.
gray_cover = cv2.cvtColor(cv_cover, cv2.COLOR_BGR2GRAY)

# Define noise levels (standard deviation values: 0, 10, 20, …, 100)
noise_levels = range(0, 101, 10)

# Lists/dictionaries to store histogram values and matching results.
histogram = []
noisy_images = {}
matches_to_plot = {}

# Iterate through defined noise levels.
for sigma in noise_levels:
    # Add Gaussian noise to the grayscale image.
    noise = np.random.normal(0, sigma, gray_cover.shape)
    noisy_img = gray_cover.astype(np.float32) + noise
    noisy_img = np.clip(noisy_img, 0, 255).astype(np.uint8)

    # Convert the noisy grayscale image to a 3-channel BGR image.
    noisy_img_bgr = cv2.cvtColor(noisy_img, cv2.COLOR_GRAY2BGR)
    noisy_images[sigma] = noisy_img  # stored for potential display of grayscale version if needed.

    # Use the original BGR image and the noisy BGR image for matching.
    matches, locs1, locs2 = matchPics(cv_cover, noisy_img_bgr)

    # For specific noise levels, store matching data for visualization.
    if sigma in [0, 30, 100]:
        plotMatches(cv_cover, noisy_img_bgr, matches, locs1, locs2)

    # Update histogram (number of matching keypoints).
    histogram.append(len(matches))

noise_levels = np.arange(0, 110, 10)
# Define bin edges so that each bin is centered on the noise level.
# For noise_levels 0, 10, …, 100, we can choose edges halfway between values.
bin_edges = np.arange(-5, 106, 10)  # edges: [-5, 5, 15, …, 105]

plt.figure()
plt.hist(noise_levels, bins=bin_edges, weights=histogram, color='green', rwidth=1)
plt.xlabel('Gaussian Noise Sigma')
plt.ylabel('Matching Keypoints')
plt.title('BRIEF and Noise Levels')
plt.show()


