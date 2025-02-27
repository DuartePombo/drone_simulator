import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

from physics.drone_physics import DronePhysics
from rendering.camera import FPVCamera
from rendering.drone_renderer import DroneRenderer
from rendering.hud import HUD
from environment.environment import Environment
from input.controller import ControllerInput

      
class DroneSimulator:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1024, 768
        pygame.display.set_caption("FPV Drone Simulator - Race Gates")
        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        self.font = pygame.font.SysFont('Arial', 16)
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.5, 0.7, 1.0, 1.0)  # Sky blue
        glMatrixMode(GL_PROJECTION)
        gluPerspective(90, self.width/self.height, 0.1, 1000.0)
        self.drone_physics = DronePhysics()
        self.environment = Environment()
        self.controller = ControllerInput()
        self.camera = FPVCamera(self.drone_physics)
        self.renderer = DroneRenderer(self.drone_physics)
        self.hud = HUD(self.screen, self.font, self.drone_physics)
        self.running = True
        self.paused = False
        self.clock = pygame.time.Clock()
        self.fps = 120
        self.physics_accumulator = 0.0
        self.third_person_view = False
        self.sensitivity_step = 0.01

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if event.key == pygame.K_r:
                        self.drone_physics.position = np.array([0.0, 0.0, 5.0])
                        self.drone_physics.velocity = np.array([0.0, 0.0, 0.0])
                        self.drone_physics.rotation = np.array([0.0, 0.0, 0.0])
                        self.drone_physics.angular_velocity = np.array([0.0, 0.0, 0.0])
                    if event.key == pygame.K_v:
                        self.third_person_view = not self.third_person_view
                    
                    # Sensitivity adjustment keys
                    if event.key == pygame.K_1:
                        self.drone_physics.adjust_sensitivity('roll', -self.sensitivity_step)
                    if event.key == pygame.K_2:
                        self.drone_physics.adjust_sensitivity('roll', self.sensitivity_step)
                    if event.key == pygame.K_3:
                        self.drone_physics.adjust_sensitivity('pitch', -self.sensitivity_step)
                    if event.key == pygame.K_4:
                        self.drone_physics.adjust_sensitivity('pitch', self.sensitivity_step)
                    if event.key == pygame.K_5:
                        self.drone_physics.adjust_sensitivity('yaw', -self.sensitivity_step)
                    if event.key == pygame.K_6:
                        self.drone_physics.adjust_sensitivity('yaw', self.sensitivity_step)
            
            # Update controller input - no arming check needed
            throttle, roll, pitch, yaw = self.controller.update()
            
            # Process physics - no arming check needed
            dt = self.clock.tick(self.fps) / 1000.0
            self.fps = self.clock.get_fps()
            
            if not self.paused:
                self.physics_accumulator += dt
                while self.physics_accumulator >= self.drone_physics.dt:
                    self.drone_physics.apply_controller_input(throttle, roll, pitch, yaw)
                    self.drone_physics.update()
                    self.environment.check_collisions(self.drone_physics)
                    self.physics_accumulator -= self.drone_physics.dt
            
            # Render the scene
            self.render()
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        if self.third_person_view:
            # Third-person view - position the camera behind and above the drone
            drone_pos = self.drone_physics.position
            
            # Position camera behind and above the drone
            camera_offset = np.array([-5.0, 0.0, 3.0])  # behind and above
            camera_pos = drone_pos + camera_offset
            
            # Look at the drone
            gluLookAt(
                camera_pos[0], camera_pos[1], camera_pos[2],
                drone_pos[0], drone_pos[1], drone_pos[2],
                0, 0, 1  # z is up
            )
        else:
            # First-person view from the drone's perspective
            cam_pos, look_at, up_vector = self.camera.get_view_matrix()
            gluLookAt(
                cam_pos[0], cam_pos[1], cam_pos[2],
                look_at[0], look_at[1], look_at[2],
                up_vector[0], up_vector[1], up_vector[2]
            )
        
        # Render the environment
        self.environment.render()
        
        # Always render the drone in third-person view
        if self.third_person_view:
            self.renderer.render()
            
        # Draw the HUD
        self.draw_hud()

    def draw_hud(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        self.hud.render(self.controller, self.fps)  # Pass controller, not self
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

if __name__ == "__main__":
    simulator = DroneSimulator()
    simulator.run()