import numpy as np
import os
import time

R = 5
r = 1

# trace out the circle
thetas = np.arange(0, 2 * np.pi, 0.05)
circle = np.array([
    r * np.cos(thetas),
    np.zeros(thetas.shape),
    r * np.sin(thetas)
])

# set up the normals for the circle
normals = circle.copy() / r

# offset the circle
circle[0] += 5

# trace out the torus
def X_rotation_matrix(theta):
    c = np.cos(theta)
    s = np.sin(theta)
    m = np.zeros((len(theta),3,3))
    m[:,0,0] = 1
    m[:,1:,1:] = np.array([
        [c,-s],
        [s,c],
    ]).transpose(2,0,1)
    return m

def Z_rotation_matrix(theta):
    c = np.cos(theta)
    s = np.sin(theta)
    m = np.zeros((len(theta),3,3))
    m[:,2,2] = 1
    m[:,:2,:2] = np.array([
        [c,-s],
        [s,c],
    ]).transpose(2,0,1)
    return m

m = Z_rotation_matrix(thetas)

torus = (m @ circle).transpose(0,2,1).reshape(-1,3)

# set up the normals for the torus
normals = (m @ normals).transpose(0,2,1).reshape(-1,3)

camera = np.array([-10,0,6])
screen_distance = 1
view_direction = np.array([1,0,-1])
view_direction = view_direction / np.linalg.norm(view_direction)

# set up lighting
light_direction = np.array([0,-4,-1])

# the plane of the screen is described by two vectors, both orthogonal to the viewing direction
# the left-right vector must be orthogonal to the viewing direction and z-axis
lr = np.cross(view_direction, np.array([0,0,1]))
lr = lr / np.linalg.norm(lr)

# the top-bottom axis must be orthonormal to the left_right axis and viewing direction
tb = np.cross(lr, view_direction)
tb = tb / np.linalg.norm(tb)

# greyscale for shading
greyscale =  ' .:-=+*#%@'

while(True):
    torus = torus @ X_rotation_matrix([0.05])[0]
    normals = normals @ X_rotation_matrix([0.05])[0]

    torus = torus @ Z_rotation_matrix([0.1])[0]
    normals = normals @ Z_rotation_matrix([0.1])[0]

    # project the torus on the screen
    proj_tb = screen_distance * ((torus - camera) @ tb) / ((torus - camera) @ view_direction)
    proj_lr = screen_distance * ((torus - camera) @ lr) / ((torus - camera) @ view_direction)

    # calculate shading for every point
    shading = -(normals @ light_direction)
    shading = shading + shading.min()

    # sort the points on distance to camera so only the closest points are shown
    distance_to_camera = torus @ view_direction
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
        screen[x,y] = greyscale[shade]

    os.system('cls')

    # print to terminal
    for row in np.flip(screen.T, axis=0):
        print(''.join(row))

    time.sleep(0.01)