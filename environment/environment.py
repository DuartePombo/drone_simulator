import numpy as np
from OpenGL.GL import *
import math
from environment.gate import DroneGate


class Environment:
    def __init__(self):
        self.world_size = 100.0  # meters
        self.gates = []
        self.ground_height = 0.0
        self.generate_gates(10)  # Generate 10 gates

    def generate_gates(self, count):
        for i in range(count):
            # Create gates in a rough circular pattern
            angle = (i / count) * 2 * math.pi
            radius = 20.0  # Distance from center
            
            # Calculate position
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = 5.0  # Height above ground
            
            # Make gate face toward center
            rotation = math.degrees(angle) + 90
            
            # Add some variation to heights
            if i % 2 == 0:
                z += 2.0
            
            self.gates.append(DroneGate([x, y, z], size=3.0, rotation=rotation))

    def check_collisions(self, drone):
        drone_pos = drone.position
        
        # Check collisions with gates
        for gate in self.gates:
            if gate.check_collision(drone_pos, drone.size):
                # Collision response - can be improved but works for now
                direction = drone_pos - gate.position
                distance = np.linalg.norm(direction)
                if distance > 0:  # Avoid division by zero
                    direction = direction / distance
                    drone.position += direction * 0.3  # Smaller push back
                    drone.velocity *= 0.8  # Less velocity reduction
                    # Reduce random spin for more predictable response
                    drone.angular_velocity += (np.random.random(3) - 0.5) * 0.3
                return True

        # Check world boundaries
        for i in range(3):
            if abs(drone.position[i]) > self.world_size/2:
                drone.position[i] = np.sign(drone.position[i]) * self.world_size/2
                drone.velocity[i] = -drone.velocity[i] * 0.7
                return True

        return False

    def render(self):
        # Render the ground as a grid of quads
        glBegin(GL_QUADS)
        glColor3f(0.2, 0.6, 0.2)  # Green ground
        grid_size = 100
        for x in range(-grid_size, grid_size, 10):
            for y in range(-grid_size, grid_size, 10):
                glVertex3f(x, y, self.ground_height)
                glVertex3f(x+10, y, self.ground_height)
                glVertex3f(x+10, y+10, self.ground_height)
                glVertex3f(x, y+10, self.ground_height)
        glEnd()

        # Render gates
        for gate in self.gates:
            gate.render()