import numpy as np
import cv2
from matchPics import matchPicsORB
from planarH import computeH_ransac
import matplotlib.pyplot as plt

# 1) Load source (cover) and target (desk) images.
cover_img = cv2.imread('../data/cv_cover.jpg')
desk_img  = cv2.imread('../data/cv_desk.png')

# 2) Detect ORB features and match between cover and desk.
matches, cover_keypoints, desk_keypoints = matchPicsORB(cover_img, desk_img)

# 3) Prepare to record the average inlier counts for different RANSAC budgets.
iteration_steps = range(1, 241, 30)
average_inliers = []

# 4) For each RANSAC iteration limit, estimate homography repeatedly to get a stable average.
for max_iterations in iteration_steps:
    total_inliers = 0

    # Repeat multiple times to smooth out randomness.
    for trial in range(10):
        homography, inlier_mask = computeH_ransac(
            cover_keypoints, desk_keypoints,
            max_iters=max_iterations,
            threshold=2
        )
        total_inliers += np.sum(inlier_mask)

    # Compute mean inliers over the trials.
    mean_inliers = total_inliers / 10
    average_inliers.append(mean_inliers)

# 5) Plot how the average number of inliers grows with more RANSAC iterations.
plt.figure()
plt.plot(iteration_steps, average_inliers, marker='o')
plt.xlabel('Maximum RANSAC Iterations')
plt.ylabel('Average Inliers')
plt.title('RANSAC Inliers vs Iteration Budget')
plt.savefig('../result/RANSAC.png')
