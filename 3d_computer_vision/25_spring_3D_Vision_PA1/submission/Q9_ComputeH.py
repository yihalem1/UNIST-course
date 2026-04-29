import numpy as np
import cv2
from planarH import computeH, warpPerspective, compositeH
from matchPics import matchPicsORB, matchPics

# Load the cover (source) and desk (target) images.
cover_image = cv2.imread('../data/cv_cover.jpg')
desk_image  = cv2.imread('../data/cv_desk.png')

# cover_keypoints and desk_keypoints contain the coordinates of the matching features.
matches, cover_keypoints, desk_keypoints = matchPicsORB(cover_image, desk_image)

# Compute the homography matrix (H_desk_to_cover) that maps points from the desk image to the cover image.
H_desk_to_cover = computeH(cover_keypoints, desk_keypoints)

# The warped image dimensions match those of the desk image.
warped_cover, warp_mask = warpPerspective(cover_image, H_desk_to_cover, (desk_image.shape[0], desk_image.shape[1]))

# Save the results.
cv2.imwrite('../result/wrapped_image.jpg', warped_cover)
