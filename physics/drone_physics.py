import numpy as np
import math
from utils.math_utils import rotation_matrix_from_euler

class DronePhysics:
    def __init__(self):
        # Drone physical properties
        self.mass = 0.5  # kg
        self.size = 0.25  # meters
        self.drag_coefficient = 0.5
        self.max_motor_thrust = 3.0  # Newtons
        self.position = np.array([0.0, 0.0, 5.0])  # x, y, z (meters)
        self.velocity = np.array([0.0, 0.0, 0.0])  # m/s
        self.acceleration = np.array([0.0, 0.0, 0.0])  # m/s²
        # Use a consistent order: roll, pitch, yaw (radians)
        self.rotation = np.array([0.0, 0.0, 0.0])
        self.angular_velocity = np.array([0.0, 0.0, 0.0])  # rad/s
        
        # Added angular damping to prevent roll accumulation
        self.angular_damping = 2.0  # Higher values mean more air resistance for rotation

        # Motor properties
        self.motor_forces = np.array([0.0, 0.0, 0.0, 0.0])  # % of max thrust
        self.motor_positions = np.array([
            [-self.size, -self.size, 0],  # motor 1: front left
            [self.size, -self.size, 0],   # motor 2: front right
            [self.size, self.size, 0],    # motor 3: rear right
            [-self.size, self.size, 0]    # motor 4: rear left
        ])

        # Constants
        self.g = 9.81  # gravity acceleration (m/s²)
        self.dt = 0.01  # physics time step (s)
        self.moment_of_inertia = np.array([0.01, 0.01, 0.02])  # kg·m²

        # Control sensitivity settings
        self.roll_sensitivity = 0.3  # Reduced from 0.5
        self.pitch_sensitivity = 0.3  # Reduced from 0.5
        self.yaw_sensitivity = 2  

        # Battery simulation
        self.battery_capacity = 1500  # mAh
        self.battery_remaining = 1500  # mAh
        self.battery_voltage = 3.7 * 4  # 4S LiPo (V)
        self.power_consumption_rate = 0.0  # mAh/s

    def apply_controller_input(self, throttle, roll, pitch, yaw):
        # Fix throttle mapping: -1.0 should be zero thrust, 1.0 should be max thrust
        # Map from -1.0,1.0 to 0.0,1.0 correctly
        throttle_normalized = (throttle + 1.0) / 2.0
        
        # Calculate base thrust for all motors
        thrust_base = throttle_normalized * self.max_motor_thrust

        # Apply roll (right stick left/right) with adjusted sensitivity
        roll_force = roll * self.roll_sensitivity * thrust_base

        # Apply pitch (right stick up/down) with adjusted sensitivity 
        pitch_force = pitch * self.pitch_sensitivity * thrust_base

        # Apply yaw (left stick left/right) with adjusted sensitivity
        yaw_force = yaw * self.yaw_sensitivity * thrust_base

        # Calculate individual motor forces (assuming a quad in an X configuration)
        # Front left
        self.motor_forces[0] = thrust_base - roll_force + pitch_force - yaw_force
        # Front right
        self.motor_forces[1] = thrust_base + roll_force + pitch_force + yaw_force
        # Rear right
        self.motor_forces[2] = thrust_base + roll_force - pitch_force - yaw_force
        # Rear left
        self.motor_forces[3] = thrust_base - roll_force - pitch_force + yaw_force

        # Ensure motor forces are within limits
        self.motor_forces = np.clip(self.motor_forces, 0, self.max_motor_thrust)

        # Calculate power consumption based on motor forces
        power_draw = np.sum(self.motor_forces) * 0.1
        self.power_consumption_rate = power_draw * 10  # mAh/s

    def update(self):
        # Update battery
        self.battery_remaining -= self.power_consumption_rate * self.dt
        self.battery_remaining = max(0, self.battery_remaining)
        if self.battery_remaining <= 0:
            self.motor_forces = np.zeros(4)

        # Calculate forces and torques from motors
        total_force = np.sum(self.motor_forces)

        # Calculate lift force (assuming it's aligned with the drone's z-axis)
        rotation_matrix = self.get_rotation_matrix()
        lift_vector = rotation_matrix @ np.array([0, 0, 1])
        lift_force = lift_vector * total_force

        # Calculate torques
        torque = np.zeros(3)
        for i in range(4):
            motor_force_vector = np.array([0, 0, self.motor_forces[i]])
            r = self.motor_positions[i]
            motor_torque_direction = 1 if i % 2 == 0 else -1
            motor_torque = np.array([0, 0, motor_torque_direction * self.motor_forces[i] * 0.3]) # adjust *constant for yaw strength
            position_torque = np.cross(r, motor_force_vector)
            torque += position_torque + motor_torque

        # Gravity and drag forces
        gravity_force = np.array([0, 0, -self.mass * self.g])
        drag_force = -self.drag_coefficient * self.velocity * np.abs(self.velocity)

        total_force_vector = lift_force + gravity_force + drag_force
        self.acceleration = total_force_vector / self.mass
        
        # Add angular damping (air resistance for rotation)
        angular_damping_force = -self.angular_damping * self.angular_velocity * np.abs(self.angular_velocity)
        angular_acceleration = torque / self.moment_of_inertia + angular_damping_force

        # Semi-implicit Euler integration for position and velocity
        self.velocity += self.acceleration * self.dt
        self.position += self.velocity * self.dt

        # Update angular velocity in the drone's local frame
        self.angular_velocity += angular_acceleration * self.dt
        
        # Extract current Euler angles
        roll, pitch, yaw = self.rotation
        
        # Create a transformation matrix to convert local angular velocity to Euler angle rates
        # This handles the conversion from body-frame angular velocities to Euler angle rates
        # Avoid division by zero in case pitch approaches ±90 degrees
        cp = max(abs(math.cos(pitch)), 0.001) * math.copysign(1, math.cos(pitch))
        
        transform = np.array([
            [1, math.sin(roll) * math.tan(pitch), math.cos(roll) * math.tan(pitch)],
            [0, math.cos(roll), -math.sin(roll)],
            [0, math.sin(roll) / cp, math.cos(roll) / cp]
        ])
        
        # Get Euler angle rates
        euler_rates = transform @ self.angular_velocity
        
        # Update Euler angles
        self.rotation += euler_rates * self.dt
        
        # Constrain roll and pitch to avoid gimbal lock issues
        # This limits the drone from flipping completely over
        self.rotation[0] = np.clip(self.rotation[0], -math.pi/2 + 0.1, math.pi/2 - 0.1)
        self.rotation[1] = np.clip(self.rotation[1], -math.pi/2 + 0.1, math.pi/2 - 0.1)
        
        # Normalize yaw angle (keeping yaw between 0 and 2π)
        self.rotation[2] = self.rotation[2] % (2 * math.pi)

        # Improved ground collision detection
        if self.position[2] < 0.1:  # Slightly above ground to prevent clipping
            self.position[2] = 0.1
            if self.velocity[2] < 0:  # Only reflect velocity if moving downward
                self.velocity[2] = -self.velocity[2] * 0.3  # 30% bounce
                # Apply more damping to horizontal velocity during ground contact
                self.velocity[0] *= 0.8
                self.velocity[1] *= 0.8
                self.angular_velocity *= 0.8  # Dampen rotation on ground contact
                
            landing_velocity = np.linalg.norm(self.velocity)
            if landing_velocity > 3.0:
                # Hard landing - more energy loss
                self.velocity *= 0.1
                self.angular_velocity *= 0.1

    def get_rotation_matrix(self):
        """
        Get the current rotation matrix based on drone's orientation.
        """
        roll, pitch, yaw = self.rotation
        return rotation_matrix_from_euler(roll, pitch, yaw)
    

    def adjust_sensitivity(self, control, amount):
        """
        Adjust the sensitivity of a specific control
        control: 'roll', 'pitch', or 'yaw'
        amount: positive to increase, negative to decrease
        """
        if control == 'roll':
            self.roll_sensitivity = max(0.01, min(1.0, self.roll_sensitivity + amount))
        elif control == 'pitch':
            self.pitch_sensitivity = max(0.01, min(1.0, self.pitch_sensitivity + amount))
        elif control == 'yaw':
            self.yaw_sensitivity = max(0.01, min(1.0, self.yaw_sensitivity + amount))