import pygame

class ControllerInput:
    def __init__(self):
        self.throttle = -1.0  # Left stick Y-axis (-1 to 1)
        self.yaw = 0.0        # Left stick X-axis (-1 to 1)
        self.pitch = 0.0      # Right stick Y-axis (-1 to 1)
        self.roll = 0.0       # Right stick X-axis (-1 to 1)
        self.mode = "acro"    # Always in acro mode
        
        # Input smoothing - keep track of previous values for smooth interpolation
        self.prev_values = {
            'roll': 0.0,
            'pitch': 0.0,
            'yaw': 0.0
        }
        self.smoothing_factor = 0.2  # Higher value = more smoothing
        
        # Initialize joystick subsystem
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Controller detected: {self.joystick.get_name()}")
            print(f"Joystick axes: {self.joystick.get_numaxes()}, buttons: {self.joystick.get_numbuttons()}")
            print("Throttle should be at -1.0 (no thrust) when stick is at rest")
        else:
            print("No controller detected. Simulation will not respond to input.")
    
    def update(self):
        # Default values if no joystick is connected
        if not self.joystick:
            return self.throttle, self.roll, self.pitch, self.yaw
        
        # Read raw axis values
        # Note: The axis indices may need to be adjusted based on your specific controller
        throttle_val = self.joystick.get_axis(0)
        yaw_val = self.joystick.get_axis(3)
        pitch_val = self.joystick.get_axis(2)
        roll_val = self.joystick.get_axis(1)
        
        # Debug print the raw joystick values
        print(f"Joystick raw values: throttle={throttle_val:.2f}, yaw={yaw_val:.2f}, pitch={pitch_val:.2f}, roll={roll_val:.2f}")
        
        # Assign to our variables (inverting as necessary based on controller mapping)
        self.throttle = throttle_val  # Throttle not inverted
        
        # Apply smoothing to roll, pitch, and yaw for less jerky movement
        self.roll = self.smooth_input('roll', -roll_val) # Roll is inverted in my controller
        self.pitch = self.smooth_input('pitch', pitch_val)  
        self.yaw = self.smooth_input('yaw', yaw_val)
        
        # Apply a small deadzone for better control
        for attr in ['throttle', 'yaw', 'pitch', 'roll']:
            value = getattr(self, attr)
            if abs(value) < 0.05:
                setattr(self, attr, 0.0)
        
        return self.throttle, self.roll, self.pitch, self.yaw
    
    def smooth_input(self, control, raw_value):
        """Apply smoothing to an input control value"""
        # Apply a weighted average between the current and previous value
        smoothed = self.prev_values[control] * self.smoothing_factor + raw_value * (1 - self.smoothing_factor)
        self.prev_values[control] = smoothed
        return smoothed

    def get_raw_values(self):
        """Return the raw joystick values for display purposes"""
        if not self.joystick:
            return -1.0, 0.0, 0.0, 0.0  # Default values
            
        # Read raw values directly from joystick
        throttle = -self.joystick.get_axis(0)  # Invert throttle
        yaw = self.joystick.get_axis(3)
        pitch = -self.joystick.get_axis(2)  # Invert pitch
        roll = self.joystick.get_axis(1)
        
        return throttle, roll, pitch, yaw
