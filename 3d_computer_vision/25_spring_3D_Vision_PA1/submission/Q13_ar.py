import numpy as np
import cv2
from loadVid import loadVid
from matchPics import matchPics
from planarH import computeH_ransac, compositeH
from tqdm import tqdm

# 1) Load the cover image and both videos as frame sequences
cv_cover = cv2.imread('../data/cv_cover.jpg')
panda    = loadVid('../data/ar_source.mov')
book     = loadVid('../data/book.mov')

# 2) Query the source video's frame rate so we can use it for our VideoWriter
cap = cv2.VideoCapture('../data/ar_source.mov')
fps = cap.get(cv2.CAP_PROP_FPS)
cap.release()

# 3) Grab dimensions from one of the frames (both videos should share the same resolution here)
height, width = book[0].shape[:2]

# 4) Create the VideoWriter with the same fps as ar_source.mov
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(
    '../result/ar.avi',
    fourcc,
    fps,
    (width, height)
)

# 5) Build the AR video frame by frame
for i in tqdm(range(len(panda))):
    # 5.1) Match features between the cover and this book frame
    matches, locs1, locs2 = matchPics(cv_cover, book[i])
    H2to1, _ = computeH_ransac(
        locs1[matches[:, 0]],
        locs2[matches[:, 1]],
        10,
        2
    )

    # 5.2) Crop+resize the panda frame to fit the cover
    cropped_panda = panda[i][45:310, width // 3 : -width // 3]
    cropped_panda = cv2.resize(
        cropped_panda,
        (cv_cover.shape[1], cv_cover.shape[0]),
        interpolation=cv2.INTER_LINEAR
    )

    # 5.3) Warp & overlay onto the book frame
    composite = compositeH(H2to1, cropped_panda, book[i])

    # 5.4) Write out the composite frame
    out.write(composite)

# 6) Finalize
out.release()
