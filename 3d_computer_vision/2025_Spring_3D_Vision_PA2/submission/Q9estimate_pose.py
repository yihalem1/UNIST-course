import numpy as np
import numpy.linalg as la

# Q9

class Q9():
    # DO NOT CHANGE HERE!
    def __init__(self):

        # Generate random camera matrix
        K = np.array([[1,0,100], [0,1,100], [0,0,1]])
        R, _,_ = la.svd(np.random.randn(3,3))
        if la.det(R) < 0: R = -R
        t = np.vstack((np.random.randn(2,1), 1))

        P = K @ np.hstack((R, t))

        # Generate random 2D and 3D points
        N = 100
        X = np.random.randn(N,3)
        x = P @ np.hstack((X, np.ones((N,1)))).T
        x = x[:2,:].T / np.vstack((x[2,:], x[2,:])).T

        # Test pose estimation with clean points
        Pc = self.estimate_pose(x, X)
        xp = Pc @ np.hstack((X, np.ones((N,1)))).T
        xp = xp[:2,:].T / np.vstack((xp[2,:], xp[2,:])).T

        # Test pose estimation with noisy points
        xn = x + np.random.rand(x.shape[0], x.shape[1])
        Pn = self.estimate_pose(xn, X)

        xpn = Pn @ np.hstack((X, np.ones((N,1)))).T
        xpn = xpn[:2,:].T / np.vstack((xpn[2,:], xpn[2,:])).T

        self.P, self.K, self.R, self.t = P, K, R, t
        self.x, self.xp, self.xn, self.xpn = x, xp, xn, xpn
        self.Pc = Pc
        self.Pn = Pn

    
    """
    Q9 Camera Matrix Estimation
        [I] x, 2D points (Nx2 matrix)
            X, 3D points (Nx3 matrix)
        [O] P, camera matrix (3x4 matrix)
    """
    def estimate_pose(self, x, X):

        N = X.shape[0]
        assert N >= 6, "DLT needs at least 6 correspondences."

        # Build the 2N × 12 design matrix A (two rows per correspondence)
        A = np.zeros((2 * N, 12))
        for i in range(N):
            Xi, Yi, Zi = X[i]
            ui, vi = x[i]
            Xi_h = np.array([Xi, Yi, Zi, 1])

            # first row  (corresponding to v)
            A[2 * i] = np.hstack([np.zeros(4),  # 0 … 3
                                  -Xi_h,  # 4 … 7
                                  vi * Xi_h])  # 8 …11
            # second row (corresponding to u)
            A[2 * i + 1] = np.hstack([Xi_h,  # 0 … 3
                                      np.zeros(4),  # 4 … 7
                                      -ui * Xi_h])  # 8 …11

        # Solve  A p = 0  with SVD  →  last right-singular vector
        _, _, VH = la.svd(A)
        P = VH[-1].reshape(3, 4)

        # Normalise so that the bottom-right entry is +1 (arbitrary scale)
        if P[-1, -1] != 0:
            P = P / P[-1, -1]

        return P


if __name__ == "__main__":

    Q9 = Q9()

    print('Reprojection Error with clean 2D points:', la.norm(Q9.x-Q9.xp))
    print('Pose Error with clean 2D points:', la.norm((Q9.Pc/Q9.Pc[-1,-1])-(Q9.P/Q9.P[-1,-1])))

    print('Reprojection Error with noisy 2D points:', la.norm(Q9.xn-Q9.xpn))
    print('Pose Error with noisy 2D points:', la.norm((Q9.Pn/Q9.Pn[-1,-1])-(Q9.P/Q9.P[-1,-1])))
