import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import time
import Cursor
import State
import Shaders
import StickMan

import Definitions


display = [900, 900] # window size

lastTime = 0 # for time between frames

""" camera controls """
leftRight_acceleration = 0.
left_keyHold = False
right_keyHold = False
leftRight_cam = 0
leftRight_cap = 5.

upDown_acceleration = 0.
up_keyHold = False
down_keyHold = False
upDown_cam = 0
upDown_cap = 5.

frontBack_acceleration = 0.
front_keyHold = False
back_keyHold = False
frontBack_cam = -2
frontBack_cap = 0.2

""" parts control """
pivot = [0,0,0]
pivotSpeed = 5.
q_keyHold = False
w_keyHold = False
e_keyHold = False
r_keyHold = False
t_keyHold = False
y_keyHold = False

reset = False # reset selected part orientation
prevNext = 0 # select previous/next part

style = 0 # model visualization style

rMax = 0 # ground radius


def manage():
    global display

    global lastTime

    global leftRight_acceleration
    global left_keyHold
    global right_keyHold
    global leftRight_cam

    global upDown_acceleration
    global up_keyHold
    global down_keyHold
    global upDown_cam
    
    global frontBack_acceleration
    global front_keyHold
    global back_keyHold
    global frontBack_cam

    global q_keyHold
    global w_keyHold
    global e_keyHold
    global r_keyHold
    global t_keyHold
    global y_keyHold
    global reset
    global prevNext
    global style
    global rMax

    dt = time.clock() - lastTime
    lastTime = time.clock()
    k = 18*dt # adjust speed to time instead of frame rate

    Cursor.mouse = pygame.mouse.get_pos()

    reset = False
    prevNext = 0

    """ New events """
    for event in pygame.event.get():
        """ Exit """
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            quit()

        """ Window resize """
        if event.type == VIDEORESIZE:
            display = event.size
            # not sure what to do after...

        """ Camera controller """
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            left_keyHold = True
            if leftRight_acceleration < 0.2*leftRight_cap:
                leftRight_acceleration = 0.2*leftRight_cap
        if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
            left_keyHold = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            right_keyHold = True
            if leftRight_acceleration > -0.2*leftRight_cap:
                leftRight_acceleration = -0.2*leftRight_cap
        if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
            right_keyHold = False


        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            up_keyHold = True
            if upDown_acceleration < 0.2*upDown_cap:
                upDown_acceleration = 0.2*upDown_cap
        if event.type == pygame.KEYUP and event.key == pygame.K_UP:
            up_keyHold = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            down_keyHold = True
            if upDown_acceleration > -0.2*upDown_cap:
                upDown_acceleration = -0.2*upDown_cap
        if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
            down_keyHold = False


        if event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEUP:
            front_keyHold = True
            if frontBack_acceleration < 0.2*frontBack_cap:
                frontBack_acceleration = 0.2*frontBack_cap
        if event.type == pygame.KEYUP and event.key == pygame.K_PAGEUP:
            front_keyHold = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_PAGEDOWN:
            back_keyHold = True
            if frontBack_acceleration > -0.2*frontBack_cap:
                frontBack_acceleration = -0.2*frontBack_cap
        if event.type == pygame.KEYUP and event.key == pygame.K_PAGEDOWN:
            back_keyHold = False
        
        """ Stickman controller """ # WARNING : pygame uses qwerty by default !
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            q_keyHold = True
            pivot[0] = pivotSpeed
        elif event.type == pygame.KEYUP and event.key == pygame.K_q:
            q_keyHold = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            w_keyHold = True
            pivot[0] = -pivotSpeed
        elif event.type == pygame.KEYUP and event.key == pygame.K_w:
            w_keyHold = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            e_keyHold = True
            pivot[1] = pivotSpeed
        elif event.type == pygame.KEYUP and event.key == pygame.K_e:
            e_keyHold = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            r_keyHold = True
            pivot[1] = -pivotSpeed
        elif event.type == pygame.KEYUP and event.key == pygame.K_r:
            r_keyHold = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            t_keyHold = True
            pivot[2] = pivotSpeed
        elif event.type == pygame.KEYUP and event.key == pygame.K_t:
            t_keyHold = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_y:
            y_keyHold = True
            pivot[2] = -pivotSpeed
        elif event.type == pygame.KEYUP and event.key == pygame.K_y:
            y_keyHold = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
            reset = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            prevNext = 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
            prevNext = -1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            style = (style + 1)%4
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            State.callSave = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            State.callLoad = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_j:
            State.currentFile = (State.currentFile - 1 + len(State.fileName))%len(State.fileName)
            State.callLoad = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
            State.currentFile = (State.currentFile + 1)%len(State.fileName)
            State.callLoad = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            rMax += 1
            if rMax > 6:
                rMax = -5


    """ Camera update - left / right """
    if left_keyHold is False and right_keyHold is False:
        if leftRight_acceleration > 0.05*leftRight_cap*k:
            leftRight_acceleration -= 0.1*leftRight_cap*k
        elif leftRight_acceleration < -0.05*leftRight_cap*k:
            leftRight_acceleration += 0.1*leftRight_cap*k
        else:
            leftRight_acceleration = 0.
    elif left_keyHold is True and right_keyHold is True:
        leftRight_acceleration = 0.
    else:
        if left_keyHold is True:
            if leftRight_acceleration < leftRight_cap*k:
                leftRight_acceleration += 0.1*leftRight_cap*k
            else:
                leftRight_acceleration = leftRight_cap*k
        elif right_keyHold is True:
            if leftRight_acceleration > -leftRight_cap*k:
                leftRight_acceleration -= 0.1*leftRight_cap*k
            else:
                leftRight_acceleration = -leftRight_cap*k
            
    """ Camera update - up / down """
    if up_keyHold is False and down_keyHold is False:
        if upDown_acceleration > 0.05*upDown_cap*k:
            upDown_acceleration -= 0.1*upDown_cap*k
        elif upDown_acceleration < -0.05*upDown_cap*k:
            upDown_acceleration += 0.1*upDown_cap*k
        else:
            upDown_acceleration = 0.
    elif up_keyHold is True and down_keyHold is True:
        upDown_acceleration = 0.
    else:
        if up_keyHold is True:
            if upDown_acceleration < upDown_cap*k:
                upDown_acceleration += 0.1*upDown_cap*k
            else:
                upDown_acceleration = upDown_cap*k
        elif down_keyHold is True:
            if upDown_acceleration > -upDown_cap*k:
                upDown_acceleration -= 0.1*upDown_cap*k
            else:
                upDown_acceleration = -upDown_cap*k

    """ Camera update - front / back """
    if front_keyHold is False and back_keyHold is False:
        if frontBack_acceleration > 0.05*frontBack_cap*k:
            frontBack_acceleration -= 0.1*frontBack_cap*k
        elif frontBack_acceleration < -0.05*frontBack_cap*k:
            frontBack_acceleration += 0.1*frontBack_cap*k
        else:
            frontBack_acceleration = 0.
    elif front_keyHold is True and back_keyHold is True:
        frontBack_acceleration = 0.
    else:
        if front_keyHold is True:
            if frontBack_acceleration < frontBack_cap*k:
                frontBack_acceleration += 0.1*frontBack_cap*k
            else:
                frontBack_acceleration = frontBack_cap*k
        elif back_keyHold is True:
            if frontBack_acceleration > -frontBack_cap*k:
                frontBack_acceleration -= 0.1*frontBack_cap*k
            else:
                frontBack_acceleration = -frontBack_cap*k

    """ Apply camera control """
    frontBack_cam += frontBack_acceleration
    leftRight_cam += leftRight_acceleration
    upDown_cam += upDown_acceleration
    
    Definitions.viewMatrix.push()
    Definitions.viewMatrix.translate(0,0,frontBack_cam)
    Definitions.viewMatrix.rotate(upDown_cam, 1, 0, 0)
    Definitions.viewMatrix.rotate(leftRight_cam, 0, 1, 0)
    glUniformMatrix4fv(Shaders.view_loc, 1, GL_FALSE, Definitions.viewMatrix.peek())
    Definitions.viewMatrix.pop()

    """ parts control """
    if q_keyHold == False and w_keyHold == False:
        pivot[0] = 0
    if e_keyHold == False and r_keyHold == False:
        pivot[1] = 0
    if t_keyHold == False and y_keyHold == False:
        pivot[2] = 0
    
    """ StickMan Events """
    j = 0
    while j <  len(StickMan.selectedParts):
        i = 0
        while i <  len(StickMan.parts):
            if StickMan.selectedParts[j] == StickMan.parts[i][StickMan.Data_id]:
                if reset == True:
                    StickMan.virtuMan.parts[i][StickMan.Data_angle] = [1,0,0,0]
                if prevNext != 0:
                    StickMan.selectedParts[j] = StickMan.parts[(i+prevNext+len(StickMan.parts))% len(StickMan.parts)][StickMan.Data_id]
                break
            i += 1
        j += 1

        
    """ save/load model """
    if State.callSave == True:
        State.save(StickMan.virtuMan)
    if State.callLoad == True:
        State.load(StickMan.virtuMan)