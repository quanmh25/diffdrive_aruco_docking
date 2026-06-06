import numpy as np
from robot_controller.utils import radian_normalization

class ArucoKalmanFilter:
    def __init__(self, initial_pose, initial_cov, predict_noise, measure_noise):
        self.X_ = np.array(initial_pose, dtype=float).reshape(3, 1)  # State [x, y, yaw]
        
        # convert array 1D to matrix 3x3
        self.P_ = np.array(initial_cov, dtype=float).reshape(3, 3)
        self.Q_ = np.array(predict_noise, dtype=float).reshape(3, 3)
        self.R_ = np.array(measure_noise, dtype=float).reshape(3, 3)
        
        self.F_ = np.eye(3)
        self.B_ = np.eye(3) * -1.0
        self.H_ = np.eye(3)

    def predict(self, u):
        u_vec = np.array(u, dtype=float).reshape(3, 1)
        self.X_ = self.F_ @ self.X_ + self.B_ @ u_vec
        self.P_ = self.F_ @ self.P_ @ self.F_.T + self.Q_
        self.X_[2, 0] = radian_normalization(self.X_[2, 0])

    def update(self, z):
        z_vec = np.array(z, dtype=float).reshape(3, 1)
        y = z_vec - self.H_ @ self.X_
        y[2, 0] = radian_normalization(y[2, 0])
        
        S = self.H_ @ self.P_ @ self.H_.T + self.R_
        K = self.P_ @ self.H_.T @ np.linalg.inv(S)
        
        self.X_ = self.X_ + K @ y
        self.X_[2, 0] = radian_normalization(self.X_[2, 0])
        
        I = np.eye(3)
        self.P_ = (I - K @ self.H_) @ self.P_

    # return array [x, y, yaw]
    def get_state(self):
        return self.X_.flatten()