import numpy as np
import matplotlib.pyplot as plt
from Q7disparity import Q7

# Q8

class Q8(Q7):
    
    def __init__(self):
        super(Q8, self).__init__()

        """
        Write your own code here 

        Step 1. Load the rectify parameters from '../data/rectify.npz'.
            - M1, M2, K1p, K2p, R1p, R2p, t1p, t2p

        Step 2. Get depth map with the disparity map and the camera parameters.
            - self.get_depth()

        Step 3. Complete 'def vis_depth_map' to visualize the depth map.

        """

        # Step-1 : load rectification parameters saved by Q6rectify.py
        rect = np.load('../data/rectify.npz')
        K1p, K2p = rect['K1p'], rect['K2p']
        R1p, R2p = rect['R1p'], rect['R2p']
        t1p, t2p = rect['t1p'], rect['t2p']

        # Step-2 : depth map from disparity
        depthM = self.get_depth(self.disp,
                                K1p, K2p,
                                R1p, R2p,
                                t1p, t2p)

        # optionally mask the dark background used in earlier tasks
        depthM[self.I1 <= 40] = np.inf

        # DO NOT CHANGE BELOW THIS LINE
        self.depth = depthM

    """
    Q8 Depth Map
        [I] dispM, disparity map (H1xW1 matrix)
            K1 K2, camera matrices (3x3 matrix)
            R1 R2, rotation matrices (3x3 matrix)
            t1 t2, translation vectors (3x1 matrix)
        [O] depthM, depth map (H1xW1 matrix)
    """
    def get_depth(self, dispM, K1p, K2p, R1p, R2p, t1p, t2p):
        
        # optical centres  C = −Rᵀ t
        C1 = -R1p.T @ t1p
        C2 = -R2p.T @ t2p

        B = np.linalg.norm(C2 - C1)
        f = K1p[0, 0]

        # avoid divide-by-zero
        disp_safe = dispM.copy().astype(np.float32)
        disp_safe[disp_safe == 0] = np.nan

        depthM = f * B / disp_safe
        return depthM

    def vis_depth_map(self, depthM):
        plt.figure(figsize=(10, 10))
        plt.imshow(depthM, cmap='inferno')
        plt.title('Depth Map')
        plt.axis('off')
        plt.show()

if __name__ == "__main__":

    Q8 = Q8()
    Q8.vis_depth_map(Q8.depth)