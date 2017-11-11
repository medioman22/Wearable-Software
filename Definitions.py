import numpy as np
import math
import Events

class vector4D(object):
    """
        vector4D
        .o      rotation angle
        .xyz    rotation axis
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
        #print("norm : {}".format(norm))
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
        #result = vector4D((0,math.sqrt(1/3.),math.sqrt(1/3.),math.sqrt(1/3.)))
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


    #def QuatSat(self, saturation = (0, 0, 0, 0, 0, 0)):
    #    """ apply angle constraints """
    #    if math.fabs(self.o) > 0.0001:
    #        """ isolate x rotation """
    #        Q = self
    #        result = Q
    #        Dx = 1./math.sqrt(Q.o*Q.o + Q.x*Q.x)
    #        Qx = vector4D((Q.o*Dx, Q.x*Dx, 0, 0))
    #        if Qx.x < 0:
    #            Qx = vector4D.QuatFlip(Qx)
    #        """ determinate angle of rotation """
    #        Vx = vector4D.Quat2Vec(Qx)
    #        if Vx.o > 180:
    #            Vx.o -= 360
    #        """ apply constraint to x """
    #        if Vx.o >= 0 and Vx.o > saturation[0]:
    #            Vx.o = saturation[0]
    #        elif Vx.o < 0 and Vx.o < saturation[1]:
    #            Vx.o = saturation[1]
    #        dQx = vector4D.Vec2Quat(Vx)
    #
    #        Q = vector4D.QuatProd(Q, vector4D.QuatConj(Qx))
    #        Dy = 1./math.sqrt(Q.o*Q.o + Q.y*Q.y)
    #        Qy = vector4D((Q.o*Dy, 0, Q.y*Dy, 0))
    #        if Qy.y < 0:
    #            Qy = vector4D.QuatFlip(Qy)
    #        """ determinate angle of rotation """
    #        Vy = vector4D.Quat2Vec(Qy)
    #        if Vy.o > 180:
    #            Vy.o -= 360
    #        """ apply constraint to x """
    #        if Vy.o >= 0 and Vy.o > saturation[2]:
    #            Vy.o = saturation[2]
    #        elif Vy.o < 0 and Vy.o < saturation[3]:
    #            Vy.o = saturation[3]
    #        dQy = vector4D.Vec2Quat(Vy)
    #
    #        Q = vector4D.QuatProd(Q, vector4D.QuatConj(Qy))
    #        Dz = 1./math.sqrt(Q.o*Q.o + Q.z*Q.z)
    #        Qz = vector4D((Q.o*Dz, 0, 0, Q.z*Dz))
    #        if Qz.z < 0:
    #            Qz = vector4D.QuatFlip(Qz)
    #        """ determinate angle of rotation """
    #        Vz = vector4D.Quat2Vec(Qz)
    #        if Vz.o > 180:
    #            Vz.o -= 360
    #        """ apply constraint to x """
    #        if Vz.o >= 0 and Vz.o > saturation[4]:
    #            Vz.o = saturation[4]
    #        elif Vz.o < 0 and Vz.o < saturation[5]:
    #            Vz.o = saturation[5]
    #        dQz = vector4D.Vec2Quat(Vz)
    #
    #        """ build back quaternion """
    #        result = vector4D.QuatProd(vector4D.QuatProd(result, vector4D.QuatConj(Qx)), dQx) # "replace old rotation (Qx) by new rotation (dQx)"
    #        result = vector4D.QuatProd(vector4D.QuatProd(result, vector4D.QuatConj(Qy)), dQy) # "replace old rotation (Qy) by new rotation (dQy)"
    #        result = vector4D.QuatProd(vector4D.QuatProd(result, vector4D.QuatConj(Qz)), dQz) # "replace old rotation (Qz) by new rotation (dQz)"
    #        vector4D.QuatNorm(result)
    #
    #        return result
    #    else:
    #        return self

    
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
            yp = Vswing.o*math.cos(theta) + Events.pivot[1] #-math.pi/2
            zp = Vswing.o*math.sin(theta) + Events.pivot[2] #-math.pi/2
            theta = math.atan2(zp, yp)
            k = 1./math.sqrt(Ez*Ez*math.cos(theta)*math.cos(theta) + Ey*Ey*math.sin(theta)*math.sin(theta))
            ySat = k*Ey*Ez*math.cos(theta)
            zSat = k*Ey*Ez*math.sin(theta)
            if yp*yp/(Ey*Ey) + zp*zp/(Ez*Ez) > 1:
                yp = ySat
                zp = zSat
                theta = math.atan2(zp, yp)
            Vswing.o = math.sqrt(yp*yp + zp*zp)
            Vswing.y = math.cos(theta) #+math.pi/2
            Vswing.z = math.sin(theta) #+math.pi/2
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


I = np.array([[1, 0, 0, 0],
              [0, 1, 0, 0],
              [0, 0, 1, 0],
              [0, 0, 0, 1]])

""" transformation matrix storage for preprocessing """
packModel = 0
packParent = 1
packID = 2 # body & sensor
radius = 2 # ground
selected = 3 # body
entity = 3 # sensor
packagePreprocess = [[]]
packageIndices = [[],[],[],[]] # Ground, Body, Sensor, Link