import numpy as np
import cv2
from helper import briefMatch
from helper import computeBrief
from helper import corner_detection


def matchPics(I1, I2):
    # I1, I2 : Images to match

    # Convert Images to GrayScale
    I1_gray = cv2.cvtColor(I1, cv2.COLOR_BGR2GRAY)
    I2_gray = cv2.cvtColor(I2, cv2.COLOR_BGR2GRAY)

    # Detect Features in Both

    locs1 = corner_detection(I1_gray)
    locs2 = corner_detection(I2_gray)

    # Obtain descriptors for the computed feature locations

    desc1, locs1 = computeBrief(I1_gray, locs1)
    desc2, locs2 = computeBrief(I2_gray, locs2)

    # Match features using the descriptors

    # matches = briefMatch(desc1, desc2, ratio=0.9)
    matches = briefMatch(desc1, desc2)


    return matches, locs1, locs2


def matchPicsORB(img1, img2, num_matches=8):

	gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
	gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

	orb_detector = cv2.ORB_create()
	keypoints1, descriptors1 = orb_detector.detectAndCompute(gray1, None)
	keypoints2, descriptors2 = orb_detector.detectAndCompute(gray2, None)

	bf_matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
	raw_matches = bf_matcher.match(descriptors1, descriptors2)
	best_matches = sorted(raw_matches, key=lambda m: m.distance)[:num_matches]

	src_pts = np.array([keypoints1[m.queryIdx].pt for m in best_matches], dtype=np.float32)
	dst_pts = np.array([keypoints2[m.trainIdx].pt for m in best_matches], dtype=np.float32)

	return best_matches, src_pts, dst_pts