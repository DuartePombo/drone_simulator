import numpy as np
import math

def rotation_matrix_from_euler(roll, pitch, yaw):
    """
    Create rotation matrix from Euler angles (roll, pitch, yaw) in radians.
    Returns a 3x3 rotation matrix.
    """
    # Rotation around X-axis (roll)
    R_x = np.array([
        [1, 0, 0],
        [0, math.cos(roll), -math.sin(roll)],
        [0, math.sin(roll), math.cos(roll)]
    ])

    # Rotation around Y-axis (pitch)
    R_y = np.array([
        [math.cos(pitch), 0, math.sin(pitch)],
        [0, 1, 0],
        [-math.sin(pitch), 0, math.cos(pitch)]
    ])

    # Rotation around Z-axis (yaw)
    R_z = np.array([
        [math.cos(yaw), -math.sin(yaw), 0],
        [math.sin(yaw), math.cos(yaw), 0],
        [0, 0, 1]
    ])

    # Combined rotation matrix (yaw -> pitch -> roll)
    R = R_z @ R_y @ R_x
    return R