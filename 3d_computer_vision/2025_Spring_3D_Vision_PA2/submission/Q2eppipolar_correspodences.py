import numpy as np
import cv2
import helper as hlp
import matplotlib.pyplot as plt
from Q1eight_point import Q1

# Q2

class Q2(Q1):
    def __init__(self):
        super(Q2, self).__init__()

        """
        Write your own code here 

        Step 1. Load points in image 1 from data/temple_coords.npz
            - pts1 

        Step 2. Run epipolar_correspondences to get points in image 2
            - pts2 = self.epipolar_correspondences(self.im1, self.im2, self.F, pts1)

        """
        # Step 1: Load known points in image 1
        data = np.load('../data/temple_coords.npz')  # load pts1 from disk
        pts1 = data['pts1']  # shape: (N, 2)

        # Step 2: Compute correspondences in image 2
        pts2 = self.epipolar_correspondences(
            self.im1, self.im2, self.F, pts1
        )
        
        # DO NOT CHANGE HERE!
        self.pts1 = pts1
        self.pts2 = pts2


    """
    Q2 Epipolar Correspondences
        [I] im1, image 1 (H1xW1 matrix)
            im2, image 2 (H2xW2 matrix)
            F, fundamental matrix from image 1 to image 2 (3x3 matrix)
            pts1, points in image 1 (Nx2 matrix)
        [O] pts2, points in image 2 (Nx2 matrix)
    """
    def epipolar_correspondences(self, im1, im2, F, pts1):
        # Convert to grayscale for patch comparison
        gray1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

        h2, w2 = gray2.shape
        window = 11  # patch size: 11x11
        half = window // 2

        pts2 = np.zeros_like(pts1)

        for i, (x1, y1) in enumerate(pts1):
            # 1) Compute epipolar line l = F * [x1, y1, 1]^T
            p1 = np.array([x1, y1, 1.0])
            l = F.dot(p1)
            a, b, c = l / np.linalg.norm(l[:2])

            # 2) Extract patch around (x1, y1) in image 1
            x1i, y1i = int(round(x1)), int(round(y1))
            patch1 = gray1[
                     y1i - half:y1i + half + 1,
                     x1i - half:x1i + half + 1
                     ].astype(float)

            best_score = np.inf
            best_pt = (0, 0)

            # 3) Sample along the epipolar line within image bounds
            #    parametrize by x in [half, w2-half)
            for x2 in range(half, w2 - half):
                y2 = int(round(-(a * x2 + c) / b))
                if y2 < half or y2 >= h2 - half:
                    continue

                # 4) Extract patch around candidate (x2, y2)
                patch2 = gray2[
                         y2 - half:y2 + half + 1,
                         x2 - half:x2 + half + 1
                         ].astype(float)

                # 5) Compute similarity (Euclidean distance)
                score = np.sum((patch1 - patch2) ** 2)

                if score < best_score:
                    best_score = score
                    best_pt = (x2, y2)

            pts2[i] = best_pt

        return pts2

    

    def epipolarMatchGUI(self, I1, I2, F):
        sy, sx, sd = I2.shape
        f, [ax1, ax2] = plt.subplots(1, 2, figsize=(12, 9))
        ax1.imshow(I1)
        ax1.set_title('Select a point in this image')
        ax1.set_axis_off()
        ax2.imshow(I2)
        ax2.set_title('Verify that the corresponding point \n is on the epipolar line in this image')
        ax2.set_axis_off()
        while True:
            plt.sca(ax1)
            x, y = plt.ginput(1, mouse_stop=2)[0]
            xc, yc = int(x), int(y)
            v = np.array([[xc], [yc], [1]])
            l = F @ v
            s = np.sqrt(l[0]**2+l[1]**2)
            if s==0:
                hlp.error('Zero line vector in displayEpipolar')
            l = l / s
            if l[0] != 0:
                xs = 0
                xe = sx - 1
                ys = -(l[0] * xs + l[2]) / l[1]
                ye = -(l[0] * xe + l[2]) / l[1]
            else:
                ys = 0
                ye = sy - 1
                xs = -(l[1] * ys + l[2]) / l[0]
                xe = -(l[1] * ye + l[2]) / l[0]
            ax1.plot(x, y, '*', markersize=6, linewidth=2)
            ax2.plot([xs, xe], [ys, ye], linewidth=2)
            # draw points
            pc = np.array([[xc, yc]])
            p2 = self.epipolar_correspondences(I1, I2, F, pc)
            ax2.plot(p2[0,0], p2[0,1], 'ro', markersize=8, linewidth=2)
            plt.draw()



if __name__ == "__main__":

    Q2 = Q2()
    Q2.epipolarMatchGUI(Q2.im1, Q2.im2, Q2.F)



