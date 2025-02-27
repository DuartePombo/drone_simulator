import pygame
import numpy as np
import math


class HUD:
    def __init__(self, screen, font, drone_physics):
        self.screen = screen
        self.font = font
        self.drone_physics = drone_physics
        self.width, self.height = screen.get_size()
        
        # Create a larger font for some elements
        self.large_font = pygame.font.SysFont('Arial', 24)

    def render(self, controller, fps):
        # Draw a semi-transparent background for the top HUD
        top_hud = pygame.Surface((self.width, 120), pygame.SRCALPHA)
        top_hud.fill((0, 0, 0, 128))
        self.screen.blit(top_hud, (0, 0))
        
        # Draw a semi-transparent background for the bottom HUD
        bottom_hud = pygame.Surface((self.width, 180), pygame.SRCALPHA)
        bottom_hud.fill((0, 0, 0, 128))
        self.screen.blit(bottom_hud, (0, self.height - 180))
        
        # Display telemetry
        telemetry = [
            f"FPS: {fps:.1f}",
            f"Battery: {self.drone_physics.battery_remaining:.0f} mAh",
            f"Altitude: {self.drone_physics.position[2]:.1f} m",
            f"Velocity: {np.linalg.norm(self.drone_physics.velocity):.1f} m/s",
            f"Roll: {math.degrees(self.drone_physics.rotation[0]):.1f}°",
            f"Pitch: {math.degrees(self.drone_physics.rotation[1]):.1f}°",
            f"Yaw: {math.degrees(self.drone_physics.rotation[2]):.1f}°",
            f"Mode: {controller.mode.upper()}"
        ]
        
        # Display motor forces
        motor_info = [
            f"Motor FL: {self.drone_physics.motor_forces[0]:.2f} N",
            f"Motor FR: {self.drone_physics.motor_forces[1]:.2f} N", 
            f"Motor RR: {self.drone_physics.motor_forces[2]:.2f} N",
            f"Motor RL: {self.drone_physics.motor_forces[3]:.2f} N"
        ]
        
        # Display sensitivity settings
        sensitivity_info = [
            f"Roll Sens: {self.drone_physics.roll_sensitivity:.2f}",
            f"Pitch Sens: {self.drone_physics.pitch_sensitivity:.2f}",
            f"Yaw Sens: {self.drone_physics.yaw_sensitivity:.2f}"
        ]
        
        # Render telemetry
        y_offset = 10
        for i, text in enumerate(telemetry):
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (10 + i * 150, y_offset))
        
        # Render motor info
        y_offset = 40
        for i, text in enumerate(motor_info):
            text_surface = self.font.render(text, True, (200, 200, 200))
            self.screen.blit(text_surface, (10 + i * 200, y_offset))
        
        # Render sensitivity info
        y_offset = 70
        for i, text in enumerate(sensitivity_info):
            text_surface = self.font.render(text, True, (200, 200, 200))
            self.screen.blit(text_surface, (10 + i * 150, y_offset))
        
        # Render controls info
        controls_info = "Press 1-6 to adjust sensitivity, V for view toggle, R to reset, P to pause"
        controls_text = self.font.render(controls_info, True, (255, 255, 255))
        self.screen.blit(controls_text, (10, 100))
        
        # Draw enhanced joystick visualization at bottom of screen
        self.draw_enhanced_sticks(controller)
        
        # Draw artificial horizon
        self.draw_horizon()

    def draw_enhanced_sticks(self, controller):
        # Create an enhanced visualization of both joysticks
        # Get both processed and raw values
        throttle, roll, pitch, yaw = controller.throttle, controller.roll, controller.pitch, controller.yaw
        raw_throttle, raw_roll, raw_pitch, raw_yaw = controller.get_raw_values()
        
        # Left stick (throttle/yaw)
        left_title = self.font.render("LEFT STICK (Throttle/Yaw)", True, (255, 255, 255))
        self.screen.blit(left_title, (self.width // 4 - 100, self.height - 170))
        
        # Right stick (roll/pitch)
        right_title = self.font.render("RIGHT STICK (Roll/Pitch)", True, (255, 255, 255))
        self.screen.blit(right_title, (3 * self.width // 4 - 100, self.height - 170))
        
        # Left stick visualization (centered in left half)
        stick_radius = 60
        left_center = (self.width // 4, self.height - 90)
        
        # Background circle
        pygame.draw.circle(self.screen, (40, 40, 40), left_center, stick_radius)
        pygame.draw.circle(self.screen, (100, 100, 100), left_center, stick_radius, 2)
        
        # Crosshairs
        pygame.draw.line(self.screen, (70, 70, 70), 
                         (left_center[0] - stick_radius, left_center[1]),
                         (left_center[0] + stick_radius, left_center[1]), 1)
        pygame.draw.line(self.screen, (70, 70, 70), 
                         (left_center[0], left_center[1] - stick_radius),
                         (left_center[0], left_center[1] + stick_radius), 1)
        
        # Stick position (processed values)
        pygame.draw.circle(self.screen, (0, 255, 0),
                           (int(left_center[0] + yaw * stick_radius),
                            int(left_center[1] - throttle * stick_radius)),
                           8)
        
        # Raw stick position
        pygame.draw.circle(self.screen, (255, 255, 0),
                           (int(left_center[0] + raw_yaw * stick_radius),
                            int(left_center[1] - raw_throttle * stick_radius)),
                           4)
        
        # Right stick visualization (centered in right half)
        right_center = (3 * self.width // 4, self.height - 90)
        
        # Background circle
        pygame.draw.circle(self.screen, (40, 40, 40), right_center, stick_radius)
        pygame.draw.circle(self.screen, (100, 100, 100), right_center, stick_radius, 2)
        
        # Crosshairs
        pygame.draw.line(self.screen, (70, 70, 70), 
                         (right_center[0] - stick_radius, right_center[1]),
                         (right_center[0] + stick_radius, right_center[1]), 1)
        pygame.draw.line(self.screen, (70, 70, 70), 
                         (right_center[0], right_center[1] - stick_radius),
                         (right_center[0], right_center[1] + stick_radius), 1)
        
        # Stick position (processed values)
        pygame.draw.circle(self.screen, (0, 255, 0),
                           (int(right_center[0] + roll * stick_radius),
                            int(right_center[1] - pitch * stick_radius)),
                           8)
        
        # Raw stick position
        pygame.draw.circle(self.screen, (255, 255, 0),
                           (int(right_center[0] + raw_roll * stick_radius),
                            int(right_center[1] - raw_pitch * stick_radius)),
                           4)
        
        # Add labels
        throttle_label = self.font.render(f"Throttle: {throttle:.2f}", True, (255, 255, 255))
        yaw_label = self.font.render(f"Yaw: {yaw:.2f}", True, (255, 255, 255))
        roll_label = self.font.render(f"Roll: {roll:.2f}", True, (255, 255, 255))
        pitch_label = self.font.render(f"Pitch: {pitch:.2f}", True, (255, 255, 255))
        
        self.screen.blit(throttle_label, (left_center[0] - 60, left_center[1] + stick_radius + 10))
        self.screen.blit(yaw_label, (left_center[0] - 60, left_center[1] + stick_radius + 30))
        self.screen.blit(roll_label, (right_center[0] - 60, right_center[1] + stick_radius + 10))
        self.screen.blit(pitch_label, (right_center[0] - 60, right_center[1] + stick_radius + 30))

    def draw_horizon(self):
        horizon_width = 200
        horizon_height = 100
        horizon_x = (self.width - horizon_width) // 2
        horizon_y = self.height - horizon_height - 40  # Positioned at bottom of screen
        pygame.draw.rect(self.screen, (0, 0, 0), (horizon_x, horizon_y, horizon_width, horizon_height))
        roll = self.drone_physics.rotation[0]
        pitch = self.drone_physics.rotation[1]
        center_x = horizon_x + horizon_width // 2
        center_y = horizon_y + horizon_height // 2
        pitch_offset = pitch * 40
        pygame.draw.line(
            self.screen,
            (0, 255, 0),
            (center_x - math.cos(roll) * horizon_width,
             center_y - math.sin(roll) * horizon_width + pitch_offset),
            (center_x + math.cos(roll) * horizon_width,
             center_y + math.sin(roll) * horizon_width + pitch_offset),
            2
        )
        pygame.draw.line(self.screen, (255, 255, 255),
                         (center_x - 10, center_y),
                         (center_x + 10, center_y), 1)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (center_x, center_y - 10),
                         (center_x, center_y + 10), 1)