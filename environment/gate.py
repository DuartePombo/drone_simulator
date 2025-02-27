import numpy as np
from OpenGL.GL import *
import math

class DroneGate:
    def __init__(self, position, size=2.0, rotation=0.0):
        self.position = np.array(position)
        self.size = size
        self.rotation = rotation  # Rotation angle around Z-axis in degrees
        self.color = (0.9, 0.1, 0.1)  # Red color for gates
        self.thickness = 0.2  # Thickness of the gate frame
        
        # Precompute gate geometry for collision detection
        self.half_size = self.size / 2
        self.half_thickness = self.thickness / 2
        
        # Define the four bars of the gate in local coordinates
        self.bars = [
            # [min_x, min_y, min_z, max_x, max_y, max_z] for each bar
            # Top bar
            [-self.half_size, -self.half_size, -self.half_thickness, 
             self.half_size, -self.half_size + self.thickness, self.half_thickness],
            # Bottom bar
            [-self.half_size, self.half_size - self.thickness, -self.half_thickness, 
             self.half_size, self.half_size, self.half_thickness],
            # Left bar
            [-self.half_size, -self.half_size, -self.half_thickness, 
             -self.half_size + self.thickness, self.half_size, self.half_thickness],
            # Right bar
            [self.half_size - self.thickness, -self.half_size, -self.half_thickness, 
             self.half_size, self.half_size, self.half_thickness]
        ]

    def check_collision(self, drone_pos, drone_size):
        # Transform drone position to gate's local coordinate system
        local_pos = self.world_to_local(drone_pos)
        
        # Check if drone is within any of the gate's bars
        for bar in self.bars:
            # Expand bar bounds by drone size for collision check
            expanded_bar = [
                bar[0] - drone_size, bar[1] - drone_size, bar[2] - drone_size,
                bar[3] + drone_size, bar[4] + drone_size, bar[5] + drone_size
            ]
            
            # Check if drone center is within expanded bar bounds
            if (expanded_bar[0] <= local_pos[0] <= expanded_bar[3] and
                expanded_bar[1] <= local_pos[1] <= expanded_bar[4] and
                expanded_bar[2] <= local_pos[2] <= expanded_bar[5]):
                return True
        
        # No collision detected
        return False
    
    def world_to_local(self, world_pos):
        # Step 1: Translate to gate center
        relative_pos = world_pos - self.position
        
        # Step 2: Rotate around Z-axis by -rotation (opposite of gate rotation)
        angle_rad = math.radians(-self.rotation)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        # Apply rotation matrix
        rotated_x = relative_pos[0] * cos_angle - relative_pos[1] * sin_angle
        rotated_y = relative_pos[0] * sin_angle + relative_pos[1] * cos_angle
        
        # Create the transformed position vector
        local_pos = np.array([rotated_x, rotated_y, relative_pos[2]])
        
        return local_pos

    def render(self):
        x, y, z = self.position
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(self.rotation, 0, 0, 1)  # Rotate around Z axis
        
        glColor3f(*self.color)
        
        # Draw the gate as a square frame
        half_size = self.size / 2
        thickness = self.thickness / 2
        
        # Draw the frame using quads (top, bottom, left, right bars)
        # Top bar
        self.draw_box(-half_size, -half_size, -thickness, half_size, -half_size + self.thickness, thickness)
        # Bottom bar
        self.draw_box(-half_size, half_size - self.thickness, -thickness, half_size, half_size, thickness)
        # Left bar
        self.draw_box(-half_size, -half_size, -thickness, -half_size + self.thickness, half_size, thickness)
        # Right bar
        self.draw_box(half_size - self.thickness, -half_size, -thickness, half_size, half_size, thickness)
        
        glPopMatrix()

    def draw_box(self, x1, y1, z1, x2, y2, z2):
        # Helper function to draw a 3D box/cube
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(x1, y1, z2)
        glVertex3f(x2, y1, z2)
        glVertex3f(x2, y2, z2)
        glVertex3f(x1, y2, z2)
        
        # Back face
        glVertex3f(x1, y1, z1)
        glVertex3f(x1, y2, z1)
        glVertex3f(x2, y2, z1)
        glVertex3f(x2, y1, z1)
        
        # Top face
        glVertex3f(x1, y2, z1)
        glVertex3f(x1, y2, z2)
        glVertex3f(x2, y2, z2)
        glVertex3f(x2, y2, z1)
        
        # Bottom face
        glVertex3f(x1, y1, z1)
        glVertex3f(x2, y1, z1)
        glVertex3f(x2, y1, z2)
        glVertex3f(x1, y1, z2)
        
        # Right face
        glVertex3f(x2, y1, z1)
        glVertex3f(x2, y2, z1)
        glVertex3f(x2, y2, z2)
        glVertex3f(x2, y1, z2)
        
        # Left face
        glVertex3f(x1, y1, z1)
        glVertex3f(x1, y1, z2)
        glVertex3f(x1, y2, z2)
        glVertex3f(x1, y2, z1)
        glEnd()