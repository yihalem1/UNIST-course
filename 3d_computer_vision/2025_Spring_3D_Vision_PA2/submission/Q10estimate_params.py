import numpy as np
import numpy.linalg as la
from Q9estimate_pose import Q9

# Q10

class Q10(Q9):
    # DO NOT CHANGE HERE!
    def __init__(self):
        super(Q10, self).__init__()
        
        # Test parameter estimation with clean points
        Pc = self.Pc
        Kc, Rc, tc = self.estimate_params(Pc)

        # Test parameter estimation with noisy points
        Pn = self.Pn
        Kn, Rn, tn = self.estimate_params(Pn)

        self.Kc, self.Rc, self.tc = Kc, Rc, tc
        self.Kn, self.Rn, self.tn = Kn, Rn, tn


    """
    Q10 Camera Parameter Estimation
        [I] P, camera matrix (3x4 matrix)
        [O] K, camera intrinsics (3x3 matrix)
            R, camera extrinsics rotation (3x3 matrix)
            t, camera extrinsics translation (3x1 matrix)
    """
    def estimate_params(self, P):
        # 1.  camera centre  C  (homogeneous, last row of V from SVD)
        _, _, Vt = la.svd(P)
        C_h = Vt[-1]  # 4-vector
        C = C_h[:3] / C_h[3]  # inhomogeneous 3-vector

        # 2.  intrinsic K  and rotation R  (RQ-decomposition of M)
        M = P[:, :3]  # left 3×3 block

        # numpy has only QR, so do RQ by QR on the inverse then invert
        Q, R_inv = la.qr(la.inv(M))  # M⁻¹ = Q R_inv   ⇒   M = R_inv⁻¹ Q⁻¹
        R = la.inv(Q)
        K = la.inv(R_inv)

        # ensure K has positive diagonal (common convention)
        T = np.diag(np.sign(np.diag(K)))
        K = K @ T
        R = T @ R

        # 3.  translation  t  in camera coordinates
        t = -R @ C.reshape(3, 1)

        return K, R, t

if __name__ == "__main__":

    Q10 = Q10()

    print('Intrinsic Error with clean 2D points:', la.norm((Q10.Kc/Q10.Kc[-1,-1])-(Q10.K/Q10.K[-1,-1])))
    print('Rotation Error with clean 2D points:', la.norm(Q10.R-Q10.Rc))
    print('Translation Error with clean 2D points:', la.norm(Q10.t-Q10.tc))
    
    print('Intrinsic Error with noisy 2D points:', la.norm((Q10.Kn/Q10.Kn[-1,-1])-(Q10.K/Q10.K[-1,-1])))
    print('Rotation Error with noisy 2D points:', la.norm(Q10.R-Q10.Rn))
    print('Translation Error with noisy 2D points:', la.norm(Q10.t-Q10.tn))