import numpy as np
import math

class FPVCamera:
    def __init__(self, drone_physics):
        self.drone_physics = drone_physics
        self.fov = 90  # Field of view in degrees
        # Offset the camera slightly forward to simulate an FPV mount
        self.offset = np.array([0, 0.1, 0])
        self.camera_angle = 20  # Camera tilt angle in degrees (typical for FPV cameras)

    def get_view_matrix(self):
        # Get the drone's position and rotation
        position = self.drone_physics.position
        rotation_matrix = self.drone_physics.get_rotation_matrix()

        # Apply the camera offset
        camera_pos = position + rotation_matrix @ self.offset

        # Apply the tilt (rotate about the x-axis)
        tilt_rad = math.radians(self.camera_angle)
        tilt_matrix = np.array([
            [1, 0, 0],
            [0, math.cos(tilt_rad), -math.sin(tilt_rad)],
            [0, math.sin(tilt_rad), math.cos(tilt_rad)]
        ])

        # Combine rotations for the final view
        look_rotation = rotation_matrix @ tilt_matrix

        # Calculate the look direction and up vector
        look_dir = look_rotation @ np.array([0, 1, 0])
        up_vector = look_rotation @ np.array([0, 0, 1])
        look_at_point = camera_pos + look_dir

        return camera_pos, look_at_point, up_vector