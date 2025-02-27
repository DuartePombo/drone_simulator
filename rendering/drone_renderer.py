from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

class DroneRenderer:
    def __init__(self, drone_physics):
        self.drone_physics = drone_physics
        self.prop_rotation = [0, 0, 0, 0]  # Propeller rotation angles

    def render(self):
        pos = self.drone_physics.position
        rotation_matrix = self.drone_physics.get_rotation_matrix()
        glPushMatrix()
        glTranslatef(pos[0], pos[1], pos[2])
        gl_matrix = np.eye(4, dtype=np.float32)
        gl_matrix[:3, :3] = rotation_matrix.T  # Transpose for OpenGL
        glMultMatrixf(gl_matrix.flatten())
        
        # Draw the main body as a cross
        glBegin(GL_LINES)
        glColor3f(1.0, 1.0, 1.0)  # White body
        glVertex3f(-self.drone_physics.size, -self.drone_physics.size, 0)
        glVertex3f(self.drone_physics.size, self.drone_physics.size, 0)
        glVertex3f(-self.drone_physics.size, self.drone_physics.size, 0)
        glVertex3f(self.drone_physics.size, -self.drone_physics.size, 0)
        glEnd()

        # Draw motors and propellers
        for i, motor_pos in enumerate(self.drone_physics.motor_positions):
            glPushMatrix()
            glTranslatef(motor_pos[0], motor_pos[1], motor_pos[2])
            glColor3f(0.3, 0.3, 0.3)  # Dark gray motors
            quad = gluNewQuadric()
            gluCylinder(quad, 0.05, 0.05, 0.03, 8, 1)
            gluDeleteQuadric(quad)
            
            # Calculate propeller rotation based on motor power
            motor_power = self.drone_physics.motor_forces[i] / self.drone_physics.max_motor_thrust
            self.prop_rotation[i] += motor_power * 30.0
            self.prop_rotation[i] %= 360.0
            
            # Color code propellers
            if i == 0:  # Front left
                glColor3f(1.0, 0.0, 0.0)  # Red
            elif i == 1:  # Front right
                glColor3f(0.0, 1.0, 0.0)  # Green
            elif i == 2:  # Rear right
                glColor3f(0.0, 0.0, 1.0)  # Blue
            else:  # Rear left
                glColor3f(1.0, 1.0, 0.0)  # Yellow
                
            glRotatef(self.prop_rotation[i], 0, 0, 1)
            
            # Draw the propeller as a simple cross
            glBegin(GL_TRIANGLES)
            for j in range(2):
                angle = j * 180.0
                rad = math.radians(angle)
                glVertex3f(0, 0, 0.03)
                glVertex3f(0.10 * math.cos(rad), 0.10 * math.sin(rad), 0.03)
                glVertex3f(0.02 * math.cos(rad + 0.5), 0.02 * math.sin(rad + 0.5), 0.03)
            glEnd()
            glPopMatrix()

        # Draw a red arrow indicating the drone front
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, self.drone_physics.size * 1.5, 0)
        glEnd()

        # Draw a yellow sphere at the center
        glColor3f(1.0, 1.0, 0.0)
        quad = gluNewQuadric()
        gluSphere(quad, 0.05, 8, 8)
        gluDeleteQuadric(quad)
        glPopMatrix()