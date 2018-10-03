#
#   File : Definitions.py
#   
#   Code written by : Johann Heches
#
#   Description : Handles vector4D and matrix44 classes
#       The vector4D class is generic to hold either a quaternion, angle-axis or euler angles. With a set of methods specifically required for this project.
#       The matrix44 class is used for the model / view / projection matrix, with methods to push/pop on a stack and apply commonly used transformations.
#

import numpy as np
import math
import Events

"""
"""
class vector4D(object):
    """
        vector4D
        Can hold a quaternion, an axis-angle or an euler angle.
        has methods to convert between those as well for basic operators.

        Quaternion / axis-angle
        .o      rotation angle
        .xyz    rotation axis

        Euler angles
        .o      ~
        .xyz    euler angles
    """
    __name__ = "vector4D"
    nb__init__ = 0 # keeps track of how many creations there are


    def __init__(self, ini = (0,1,0,0)):
        """ constructor """
        vector4D.nb__init__ += 1
        self.o = ini[0]
        self.x = ini[1]
        self.y = ini[2]
        self.z = ini[3]
        

    @classmethod
    def feedback(cls,reset = False):
        """ print feedback on class calls """
        print("\n")
        print("nb__init__ : {}".format(vector4D.nb__init__))
        if reset == True:
            vector4D.nb__init__ = 0
            print("reset for {} is done".format(cls.__name__))
        

    def values(self):
        """ print vector4D values """
        print(self.o, self.x, self.y, self.z)


    def QuatNorm(self):
        """ normalize quaternion """
        norm = math.sqrt(self.o*self.o + self.x*self.x + self.y*self.y + self.z*self.z)
        if norm > 0.0001:
            self.o /= norm
            self.x /= norm
            self.y /= norm
            self.z /= norm
        else:
            print("can't normalize null quaternion !")
            exit()
        """ keep rotation positive """
        """if self.o < 0:
            self.o = -self.o
            self.x = -self.x
            self.y = -self.y
            self.z = -self.z"""

    def QuatAdd(q1, q2):
        result = vector4D()
        result.o = q1.o + q2.o
        result.x = q1.x + q2.x
        result.y = q1.y + q2.y
        result.z = q1.z + q2.z
        return result

    def QuatProd(q1, q2):
        """ multiply two quaternions """
        result = vector4D()
        result.o = q1.o*q2.o - q1.x*q2.x - q1.y*q2.y - q1.z*q2.z
        result.x = q1.o*q2.x + q1.x*q2.o + q1.y*q2.z - q1.z*q2.y
        result.y = q1.o*q2.y + q1.y*q2.o + q1.z*q2.x - q1.x*q2.z
        result.z = q1.o*q2.z + q1.z*q2.o + q1.x*q2.y - q1.y*q2.x
        return result


    def QuatConj(q):
        """ quaternion conjugate """
        result = vector4D()
        result.o = q.o
        result.x = -q.x
        result.y = -q.y
        result.z = -q.z
        return result
    
    def QuatFlip(q):
        """ quaternion flip """
        result = vector4D()
        result.o = -q.o
        result.x = -q.x
        result.y = -q.y
        result.z = -q.z
        return result

    def QuatRot(q, v):
        """ quaternion rotation """
        result = vector4D.QuatProd(vector4D.QuatProd(q,v),vector4D.QuatConj(q))
        return result

    def VecDot(v1, v2):
        """ vector dot product """
        result = v1.x*v2.x + v1.y*v2.y + v1.z*v2.z
        return result
    
    def VecCross(v1, v2):
        """ vector dot product """
        result = vector4D()
        result.o = 0
        result.x = v1.y*v2.z - v1.z*v2.y
        result.y = v1.z*v2.x - v1.x*v2.z
        result.z = v1.x*v2.y - v1.y*v2.x
        return result

    def AngleAxisBetween2Vec(v1, v2):
        v1.QuatNorm()
        v2.QuatNorm()
        result = vector4D()
        try: #prevents acos(+- 1.0002) which is math domain error
            angle = 180/math.pi*math.acos(vector4D.VecDot(v1, v2))
        except:
            angle = 0
        axis = vector4D.VecCross(v1, v2)
        result.o = angle
        result.x = axis.x
        result.y = axis.y
        result.z = axis.z
        return result

    def Vec2Quat(self, Conv2Rad = True):
        """ convert vector to quaternion """
        temp = vector4D()
        result = vector4D()
        det = math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
        if det != 0 and det != 1:
            self.x /= det
            self.y /= det
            self.z /= det
        if Conv2Rad == True:
            temp.o = math.pi/180.*self.o
        result.o = math.cos(0.5*temp.o)
        result.x = math.sin(0.5*temp.o)*self.x
        result.y = math.sin(0.5*temp.o)*self.y
        result.z = math.sin(0.5*temp.o)*self.z
        result.QuatNorm()
        return result
        

    def Quat2Vec(self, Conv2Deg = True):
        """ convert quaternion to vector """
        self.QuatNorm()
        result = vector4D((0,0,0,0))
        if self.o < 0.9999 and self.o > -0.9999:
            result.o = 2*math.acos(self.o)
            result.x = self.x/math.sqrt(1 - self.o*self.o)
            result.y = self.y/math.sqrt(1 - self.o*self.o)
            result.z = self.z/math.sqrt(1 - self.o*self.o)
            if Conv2Deg == True:
                result.o = 180/math.pi*result.o

            norm = math.sqrt(result.x*result.x + result.y*result.y + result.z*result.z)
            if norm > 0.0001:
                result.x /= norm
                result.y /= norm
                result.z /= norm
            else:
                print("failed to normalize vector !")
                #exit()
        return result


    def Eul2Quat(self, Conv2Rad = True):
        """ convert euler to quaternion """
        result = vector4D()
        if Conv2Rad == True:
            result.o = math.pi/180.*self.o
            result.x = math.pi/180.*self.x
            result.y = math.pi/180.*self.y
            result.z = math.pi/180.*self.z
        temp = result
        result.o = math.cos(0.5*temp.x)*math.cos(0.5*temp.y)*math.cos(0.5*temp.z) + math.sin(0.5*temp.x)*math.sin(0.5*temp.y)*math.sin(0.5*temp.z)
        result.x = math.sin(0.5*temp.x)*math.cos(0.5*temp.y)*math.cos(0.5*temp.z) - math.cos(0.5*temp.x)*math.sin(0.5*temp.y)*math.sin(0.5*temp.z)
        result.y = math.cos(0.5*temp.x)*math.sin(0.5*temp.y)*math.cos(0.5*temp.z) + math.sin(0.5*temp.x)*math.cos(0.5*temp.y)*math.sin(0.5*temp.z)
        result.z = math.cos(0.5*temp.x)*math.cos(0.5*temp.y)*math.sin(0.5*temp.z) - math.sin(0.5*temp.x)*math.sin(0.5*temp.y)*math.cos(0.5*temp.z)
        return result


    def Quat2Eul(self, Conv2Deg = True):
        """ convert quaternion to euler """
        """ WARNING : you better find an alternative and not convert quaternions to euler """
        self.QuatNorm()
        result = vector4D()
        result.o = 0
        result.x = math.atan2(2*(self.o*self.x + self.y*self.z), 1 - 2*(self.x*self.x + self.y*self.y))
        result.y = math.asin(2*(self.o*self.y - self.z*self.x))
        result.z = math.atan2(2*(self.o*self.z + self.x*self.y), 1 - 2*(self.y*self.y + self.z*self.z))
        if Conv2Deg == True:
            result.x *= 180./math.pi
            result.y *= 180./math.pi
            result.z *= 180./math.pi
        return result

    
    def Swing(swing, saturation = (0, 0, 0, 0, 0, 0)):
        Qswing = swing
        # swing saturation (ellipse)
        Cy = 0.5*(saturation[2]+saturation[3])
        Cz = 0.5*(saturation[4]+saturation[5])
        Ey = 0.5*(saturation[2]-saturation[3])
        Ez = 0.5*(saturation[4]-saturation[5])

        if Ey == 0:
            if Qswing.z < 0:
                Qswing = vector4D.QuatFlip(Qswing)
            Vswing = vector4D.Quat2Vec(Qswing)
            Vswing.o += Events.pivot[2]
            Vswing.x = 0
            Vswing.y = 0
            Vswing.z = 1
            
            if Vswing.o > 180:
                Vswing.o -= 360
            elif Vswing.o <= -180:
                Vswing.o += 360

            if Vswing.o > saturation[4]:
                Vswing.o = saturation[4]
            elif Vswing.o < saturation[5]:
                Vswing.o = saturation[5]
            Qswing = vector4D.Vec2Quat(Vswing)
        elif Ez == 0:
            if Qswing.y < 0:
                Qswing = vector4D.QuatFlip(Qswing)
            Vswing = vector4D.Quat2Vec(Qswing)
            Vswing.o += Events.pivot[1]
            Vswing.x = 0
            Vswing.y = 1
            Vswing.z = 0
            
            if Vswing.o > 180:
                Vswing.o -= 360
            elif Vswing.o <= -180:
                Vswing.o += 360

            if Vswing.o > saturation[2]:
                Vswing.o = saturation[2]
            elif Vswing.o < saturation[3]:
                Vswing.o = saturation[3]
            Qswing = vector4D.Vec2Quat(Vswing)
        else:
            Qoffset = vector4D.Eul2Quat(vector4D((0,0,Cy,Cz)))
            Qswing = vector4D.QuatProd(Qswing, vector4D.QuatConj(Qoffset))
            Vswing = vector4D.Quat2Vec(Qswing)
            if Vswing.y == 0 and Vswing.z == 0:
                if Events.pivot[1] != 0:
                    Vswing.y = Events.pivot[1]
                if Events.pivot[2] != 0:
                    Vswing.z = Events.pivot[2]

            # if out of saturation boundaries (ellipse form), find closest saturation point
            theta = math.atan2(Vswing.z, Vswing.y)
            yp = Vswing.o*math.cos(theta) + Events.pivot[1]
            zp = Vswing.o*math.sin(theta) + Events.pivot[2]
            theta = math.atan2(zp, yp)
            k = 1./math.sqrt(Ez*Ez*math.cos(theta)*math.cos(theta) + Ey*Ey*math.sin(theta)*math.sin(theta))
            ySat = k*Ey*Ez*math.cos(theta)
            zSat = k*Ey*Ez*math.sin(theta)
            if yp*yp/(Ey*Ey) + zp*zp/(Ez*Ez) > 1:
                yp = ySat
                zp = zSat
                theta = math.atan2(zp, yp)
            Vswing.o = math.sqrt(yp*yp + zp*zp)
            Vswing.y = math.cos(theta)
            Vswing.z = math.sin(theta)
            Qswing = vector4D.Vec2Quat(Vswing)
            Qswing = vector4D.QuatProd(Qswing, Qoffset)
        return Qswing
    def Twist(twist, saturation = (0, 0, 0, 0, 0, 0)):
        Qtwist = twist
        if Qtwist.x < 0:
            Qtwist = vector4D.QuatFlip(Qtwist)
        """ determinate angle of rotation """
        Vtwist = vector4D.Quat2Vec(Qtwist)
        Vtwist.o += Events.pivot[0]
        Vtwist.x = 1
        Vtwist.y = 0
        Vtwist.z = 0
        if Vtwist.o > 180:
            Vtwist.o -= 360
        elif Vtwist.o <= -180:
            Vtwist.o += 360
        """ apply constraint to x """
        if Vtwist.o >= 0 and Vtwist.o > saturation[0]:
            Vtwist.o = saturation[0]
        elif Vtwist.o < 0 and Vtwist.o < saturation[1]:
            Vtwist.o = saturation[1]
        Qtwist = vector4D.Vec2Quat(Vtwist)
        return Qtwist

    def quatAngle(self):
        if self.x < 0:
            self = vector4D.QuatFlip(self)
        angle = vector4D.Quat2Vec(self).o
        if angle > 180:
            angle -= 360
        elif angle <= -180:
            angle += 360
        return angle




class matrix44:
    def __init__(self, M):
        self.items = [M,]

    def isEmpty(self):
        return self.items == []
    
    def size(self):
        return len(self.items)

    def push(self):
        self.items = self.items + [self.items[len(self.items)-1],]

    def pop(self):
        self.items = self.items[:-1]

    def peek(self):
        if len(self.items)-1 >= 0:
            return self.items[len(self.items)-1]
        else:
            return []

    def set(self, M):
        
        self.items[len(self.items)-1] = M

    def translate(self,x,y,z):
        t = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 1, 0],
                      [x, y, z, 1]])
        self.items[len(self.items)-1] = np.dot(t, self.items[len(self.items)-1])

    def rotate(self,angle,rx,ry,rz):

        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        t = 1 - c
        
        # insert normalization here
        magnitude = math.sqrt(rx*rx + ry*ry + rz*rz)
        if magnitude == 0:
            return
        rx /= magnitude
        ry /= magnitude
        rz /= magnitude

        m00 = c + rx*rx*t
        m11 = c + ry*ry*t
        m22 = c + rz*rz*t
        tmp1 = rx*ry*t
        tmp2 = rz*s
        m01 = tmp1 + tmp2
        m10 = tmp1 - tmp2
        tmp1 = rx*rz*t
        tmp2 = ry*s
        m02 = tmp1 - tmp2
        m20 = tmp1 + tmp2
        tmp1 = ry*rz*t
        tmp2 = rx*s
        m12 = tmp1 + tmp2
        m21 = tmp1 - tmp2

        R = np.array([[m00, m01, m02, 0],
                      [m10, m11, m12, 0],
                      [m20, m21, m22, 0],
                      [0,   0,   0,   1]])
        self.items[len(self.items)-1] = np.dot(R, self.items[len(self.items)-1])

    def scale(self,sx,sy,sz):
        t = np.array([[sx, 0, 0, 0],
                      [0, sy, 0, 0],
                      [0, 0, sz, 0],
                      [0, 0, 0,  1]])
        self.items[len(self.items)-1] = np.dot(t, self.items[len(self.items)-1])

    def perspectiveProjection(self, fov, aspectRatio, near, far):

        f = 1./math.tan(math.radians(fov/2.))
        m00 = f/aspectRatio
        m10 = 0
        m20 = 0
        m30 = 0

        m01 = 0
        m11 = f
        m21 = 0
        m31 = 0

        m02 = 0
        m12 = 0
        m22 = (far + near)/(near - far)
        m32 = 2*far*near/(near - far)

        m03 = 0
        m13 = 0
        m23 = -1
        m33 = 0


        P = np.array([[m00, m01, m02, m03],
                      [m10, m11, m12, m13],
                      [m20, m21, m22, m23],
                      [m30, m31, m32, m33]])
        
        self.items[len(self.items)-1] = np.dot(P, self.items[len(self.items)-1])
        


"""
    The model, view and projection matrices are three separate matrices.
    Model maps from an object's local coordinate space into world space, view from world space to camera space, projection from camera to screen.
"""
projectionMatrix = matrix44(np.identity(4))
viewMatrix = matrix44(np.identity(4))
modelMatrix = matrix44(np.identity(4))

lookingAt = np.array([[0, 0, 0, 1]])
lookingAtID = 0

I = np.array([[1, 0, 0, 0],
              [0, 1, 0, 0],
              [0, 0, 1, 0],
              [0, 0, 0, 1]])
