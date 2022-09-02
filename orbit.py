import numpy as np
import time
import os

class Body():
    def __init__(self, mass, radius, position, velocity, star=False):
        self.mass = mass
        self.radius = radius
        self.position = position
        self.velocity = velocity
        self.star = star

        self.draw_sphere()
        self.normals = self.points.copy() / radius
        self.points = self.points + position

    def draw_sphere(self):
        thetas = np.arange(0, 2 * np.pi, 0.05)

        circle = np.array([
            self.radius * np.cos(thetas),
            np.zeros(thetas.shape),
            self.radius * np.sin(thetas)
        ])

        m = self.rotation_matrix(thetas)

        self.points = (m @ circle).transpose(0,2,1).reshape(-1,3)

    def rotation_matrix(self, theta):
        c = np.cos(theta)
        s = np.sin(theta)
        m = np.zeros((len(theta),3,3))
        m[:,2,2] = 1
        m[:,:2,:2] = np.array([
            [c,-s],
            [s,c],
        ]).transpose(2,0,1)
        return m

    def shade(self, star_position=None):
        if self.star:
            self.shading = np.ones(self.points.shape[0])
        else:
            light_direction = self.position - star_position
            light_direction = light_direction / np.linalg.norm(light_direction)
            self.shading = -(self.normals @ light_direction)

class Camera():
    def __init__(self, position, focus, screen_distance):
        self.position = position
        self.focus = focus
        self.screen_distance = screen_distance

        direction = focus - position
        self.direction = direction / np.linalg.norm(direction)

        left_right = np.cross(self.direction, np.array([0,0,1]))
        self.left_right = left_right / np.linalg.norm(left_right)

        top_bottom = np.cross(left_right, self.direction)
        self.top_bottom = top_bottom / np.linalg.norm(top_bottom)

        self.greyscale = ' .:-=+*#%@'

    def project(self, bodies):
        points = np.concatenate([body.points for body in bodies])
        shading = np.concatenate([body.shading for body in bodies])

        # project the torus on the screen
        proj_tb = self.screen_distance * ((points - self.position) @ self.top_bottom) \
            / ((points - self.position) @ self.direction)
        proj_lr = self.screen_distance * ((points - self.position) @ self.left_right) \
            / ((points - self.position) @ self.direction)

        # sort the points on distance to camera so only the closest points are shown
        distance_to_camera = points @ self.direction
        order = (-distance_to_camera).argsort()

        # set up the screen
        screen = np.empty((150,60), dtype='str')
        screen[:] = ' '

        # convert x, y and shading to digital values
        digital_lr = np.digitize(proj_lr, np.linspace(-1,1,screen.shape[0]))
        digital_tb = np.digitize(proj_tb, np.linspace(-1,1,screen.shape[1]))
        digital_shading = np.digitize(shading, np.linspace(shading.min(),shading.max(), 10)) - 1

        # fill the screen
        for x, y, shade in zip(digital_lr[order], digital_tb[order], digital_shading[order]):
            screen[x,y] = self.greyscale[shade]

        return np.flip(screen.T, axis=0)

c = Camera(position=np.array([-10, 0, 6]), focus=np.array([0,0,0]), screen_distance=1)
sun = Body(1,2,np.array([0,0,0]), np.array([0,0,0]), star=True)
earth = Body(1,1, np.array([-7,0,0]), np.array([0,0,0]))



while(True):
    earth.position = earth.position @ earth.rotation_matrix([0.1])[0]
    earth.points = earth.points @ earth.rotation_matrix([0.1])[0]
    earth.normals = earth.normals @ earth.rotation_matrix([0.1])[0]

    sun.shade()
    earth.shade(sun.position)
    
    

    screen = c.project([sun, earth])

    os.system('clear')
    for row in screen:
        print(''.join(row))

    time.sleep(0.01)