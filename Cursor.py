from OpenGL.GLU import *
import numpy as np


mouse = [0,0]



def barycenter(points):
    center = [0.,0.]
    for point in points:
        center[0] += point[0]
        center[1] += point[1]
    center[0] /= float(len(points))
    center[1] /= float(len(points))
    return center

def intersect(P, R, Q, S):
    R = np.subtract(R,P)
    S = np.subtract(S,Q)
    QP = np.subtract(Q,P)
    RS = np.cross(R,S)
    QPR = np.cross(QP, R)
    QPS = np.cross(QP, S)
    t = np.divide(QPS, float(RS))
    u = np.divide(QPR, float(RS))
    if RS == 0 and QPR == 0:
        #case 1 : colinear
        return [False, 0, 0] #change later to check superposition
    elif RS == 0 and QPR != 0:
        #case 2 : parallel
        return [False, 0, 0]
    elif RS != 0 and t >= 0 and t <= 1 and u >= 0 and u <= 1:
        #case 3 : one point intersection
        return [True, np.add(P, np.multiply(t, R))]
    else:
        #case 4 : no intersection
        return [False, 0, 0]

cube = [[[-0.5,-0.5,-0.5], [0.5,-0.5,-0.5],  [0.5,0.5,-0.5],  [-0.5,0.5,-0.5]],   \
        [[-0.5,-0.5,-0.5], [-0.5,-0.5,0.5],  [0.5,-0.5,0.5],  [0.5,-0.5,-0.5]],   \
        [[0.5,-0.5,-0.5],  [0.5,-0.5,0.5],   [0.5,0.5,0.5],   [0.5,0.5,-0.5] ],    \
        [[0.5,0.5,-0.5],   [0.5,0.5,0.5],    [-0.5,0.5,0.5],  [-0.5,0.5,-0.5]],   \
        [[-0.5,0.5,-0.5],  [-0.5,0.5,0.5],   [-0.5,-0.5,0.5], [-0.5,-0.5,-0.5]],  \
        [[-0.5,0.5,0.5],   [0.5,0.5,0.5],    [0.5,-0.5,0.5],  [-0.5,-0.5,0.5]]]
def mouseOnPart():
    global mouse
    i = 0
    while i < 6:
        p0 = gluProject(cube[i][0][0], cube[i][0][1], cube[i][0][2])
        p1 = gluProject(cube[i][1][0], cube[i][1][1], cube[i][1][2])
        p2 = gluProject(cube[i][2][0], cube[i][2][1], cube[i][2][2])
        p3 = gluProject(cube[i][3][0], cube[i][3][1], cube[i][3][2])
        points = [[p0[0], 900-p0[1]],[p1[0], 900-p1[1]],[p2[0], 900-p2[1]],[p3[0], 900-p3[1]]]
        ctr = barycenter(points)
        I = intersect(mouse,ctr,points[0],points[1])
        J = intersect(mouse,ctr,points[1],points[2])
        K = intersect(mouse,ctr,points[2],points[3])
        L = intersect(mouse,ctr,points[3],points[0])
        if I[0] == False and J[0] == False and K[0] == False and L[0] == False:
            return True
        i += 1
    return False