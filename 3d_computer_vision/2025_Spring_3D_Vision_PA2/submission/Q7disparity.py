import numpy as np
import helper as hlp
import matplotlib.pyplot as plt
from Q6rectify import Q6
from scipy.signal import convolve2d

class Q7(Q6):
   
    def __init__(self):
        super(Q7, self).__init__()

    
        """
        Write your own code here 

        Step 1. Get disparity with the images rectified at Q6.
            - Set 'min_disp=370' and 'num_disp=60'.
            - dispM = self.get_disparity(I1, I2, window_size, min_disp, num_disp)

        Step 2. Clamp disparity values to the range [min_disp-1, min_disp+num_disp+1].

        Step 3. Complete 'def vis_disparity_image' to visualize the disparity map.

        """
        win_size = 3
        min_disp = 370
        num_disp = 60

        print('[Q7]  computing disparity map …')
        dispM = self.get_disparity(self.I1, self.I2,
                                   win_size, min_disp, num_disp)

        # Step-2  clamp to the valid search range (helps visualisation)
        dispM = np.clip(dispM, min_disp - 1, min_disp + num_disp + 1)
        dispM[self.I1 <= 40] = np.inf

        # DO NOT CHANGE BELOW THIS LINE
        self.disp = dispM

    """
    Q7 Disparity Map
        [I] im1, image 1 (H1xW1 matrix)
            im2, image 2 (H2xW2 matrix)
            win_size, window size value
        [O] dispM, disparity map (H1xW1 matrix)
    """

    # dense window-based disparity (Σ of squared differences)
    def get_disparity(self, I1, I2, win_size, min_disp, num_disp):

        I1 = I1.astype(np.float32)
        I2 = I2.astype(np.float32)
        h, w = I1.shape
        half = win_size // 2

        # pre-build box-filter kernel  (convolution = fast sliding window SSE)
        kernel = np.ones((win_size, win_size), dtype=np.float32)

        # cost volume : H × W × D   (initialised with +∞)
        C = np.full((h, w, num_disp), np.inf, dtype=np.float32)

        for d_idx, d in enumerate(range(min_disp, min_disp + num_disp)):
            # shift I2 *right* by d ⇒ pixels that originate d px left
            shifted = np.zeros_like(I2)
            if d < w:
                shifted[:, d:] = I2[:, :-d]

            ssd = (I1 - shifted) ** 2
            cost = convolve2d(ssd, kernel, mode='same', boundary='symm')
            C[:, :, d_idx] = cost

        disp_indices = np.argmin(C, axis=2)
        dispM = min_disp + disp_indices
        dispM = dispM.astype(np.float32)

        # mask image boundaries where a full window does not fit
        dispM[:half, :] = np.inf
        dispM[-half:, :] = np.inf
        dispM[:, :half] = np.inf
        dispM[:, -half:] = np.inf
        return dispM

    # simple visualiser  (inferno = perceptually uniform)
    def vis_disparity_map(self, dispI):
        plt.figure(figsize=(8, 8))
        plt.imshow(dispI, cmap='inferno')
        plt.title('Disparity Map')
        plt.axis('off')
        plt.show()


if __name__ == "__main__":

    Q7 = Q7()
    Q7.vis_disparity_map(Q7.disp)

