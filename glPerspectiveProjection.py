#!/usr/bin/env python2.3

import OpenGL 
OpenGL.ERROR_ON_COPY = True 
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys, time 
#from math import sin,cos,sqrt,pi
from numpy import *
from OpenGL.constants import GLfloat

vec4 = GLfloat_4
(view_rotx, view_roty ,view_rotz)=(0.0, 0.0, 0.0)
(target_x, target_y, target_z)=(0.0, 0.0, 0.0)
angle = 0.0

tStart = t0 = time.time()
frames = 0
rotationRate = 1.01
fps = 0
def framerate():
    global t0, frames, fps
    t = time.time()
    frames += 1
    if t - t0 >= 1.0:
        seconds = t - t0
        fps = frames/seconds
        t0 = t
        frames = 0
    return fps

def renderStr( x, y, string):
    glRasterPos2i(x, y)

    for c in string:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c) )
               
def draw():
    global target_x, target_y, target_z

    # Skybox coordinates
    x = 30
    y = 20
    z = 800
    tea_pos = (0.0, 0.0, float(z)/4.0)
    
##    glMatrixMode(GL_PROJECTION)
##    glLoadIdentity()
##    glFrustum( -1.0, 1.0,-1.0, 1.0, 5.0, 3000.0)

    # Prepare render context
    glMatrixMode(GL_MODELVIEW)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Set perspective
    # http://pyopengl.sourceforge.net/documentation/manual/gluLookAt.3G.html
    glLoadIdentity()
    cam = ( 0+target_x, 0+target_y, -10+target_z)
    gluLookAt( cam[0], cam[1], cam[2], tea_pos[0], tea_pos[1], tea_pos[2], 0, 1, 0)

    # Render context
    glPushMatrix()

    # Tea pot (rotateable)
    glPushMatrix()
    glTranslatef( tea_pos[0], tea_pos[1], tea_pos[2])
    glRotatef(view_rotx, 1.0, 0.0, 0.0)
    glRotatef(view_roty, 0.0, 1.0, 0.0)
    glRotatef(view_rotz, 0.0, 0.0, 1.0)
    
    glColor4f(1.0, 0.55, 0.0,1.0)
    glutSolidTeapot(6)

    #quad = gluNewQuadric()
    #gluCylinder(quad, 3, 3, 6, 18, 8);
    
    glPopMatrix()

    # Render skybox
    glColor4f(0.6, 0.6, 0.6, 0.8)

    glBegin(GL_QUADS)
    # back
    glVertex3f(-x, y,-z)
    glVertex3f(-x,-y,-z)
    glVertex3f( x,-y,-z)
    glVertex3f( x, y,-z)
    # left
    glVertex3f(-x, y, z)
    glVertex3f(-x,-y, z)
    glVertex3f(-x,-y,-z)
    glVertex3f(-x, y,-z)
    # right
    glVertex3f( x, y, z)
    glVertex3f( x,-y, z)
    glVertex3f( x,-y,-z)
    glVertex3f( x, y,-z)
    # top
    glVertex3f(-x, y, z)
    glVertex3f(-x, y,-z)
    glVertex3f( x, y,-z)
    glVertex3f( x, y, z)
    # bottom
    glVertex3f(-x, -y, z)
    glVertex3f(-x, -y,-z)
    glVertex3f( x, -y,-z)
    glVertex3f( x, -y, z)
    glEnd()

    # Outlines
    x *= .99
    y *= .99
    z *= .99
    glColor4f(1.0, 0.65, 0.0,1.0)
    glLineWidth( 5.0)
    
    glBegin(GL_LINES)
    # back
    glVertex3f(-x, y,-z)
    glVertex3f(-x,-y,-z)
    glVertex3f(-x,-y,-z)
    glVertex3f( x,-y,-z)
    glVertex3f(-x, y,-z)
    glVertex3f( x, y,-z)
    glVertex3f( x, y,-z)
    glVertex3f( x,-y,-z)
    # front
    glVertex3f(-x, y, z)
    glVertex3f(-x,-y, z)
    glVertex3f(-x,-y, z)
    glVertex3f( x,-y, z)
    glVertex3f(-x, y, z)
    glVertex3f( x, y, z)
    glVertex3f( x, y, z)
    glVertex3f( x,-y, z)
    # left
    glVertex3f(-x, y,-z)
    glVertex3f(-x, y, z)
    glVertex3f(-x,-y,-z)
    glVertex3f(-x,-y, z)
    # right
    glVertex3f( x, y,-z)
    glVertex3f( x, y, z)
    glVertex3f( x,-y,-z)
    glVertex3f( x,-y, z)
    glEnd()

    glPopMatrix()


    # TEXT
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0.0, 800, 0.0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(0.20, 0.80, 0.20)

    renderStr( 10, 10, 'cam ( {}, {}, {} )'.format( cam[0], cam[1], cam[2] ) )
    renderStr( 10, 20, '{} FPS'.format( int(framerate()) ) )

    glMatrixMode(GL_MODELVIEW);
    glPopMatrix();

    glMatrixMode(GL_PROJECTION);
    glPopMatrix();

    glutSwapBuffers()

    
def idle():
    global angle
    angle += .5
    glutPostRedisplay()
    
def key(k, x, y):
    global view_rotz
    global target_x, target_y, target_z

    if k == 'z':
        view_rotz += 5.0
    elif k == 'Z':
        view_rotz -= 5.0
    elif k == 'w':
        target_y -= .1
    elif k == 's':
        target_y += .1
    elif k == 'a':
        target_x -= 0.1
    elif k == 'd':
        target_x += 0.1
    elif k == 'q':
        target_z -= 0.1
    elif k == 'e':
        target_z += 0.1
    elif ord(k) == 27: # Escape
        sys.exit(0)
    else:
        return
    glutPostRedisplay()

def special(k, x, y):
    global view_rotx, view_roty, view_rotz
    
    if k == GLUT_KEY_UP:
        view_rotx += 5.0
    elif k == GLUT_KEY_DOWN:
        view_rotx -= 5.0
    elif k == GLUT_KEY_LEFT:
        view_roty += 5.0
    elif k == GLUT_KEY_RIGHT:
        view_roty -= 5.0
    else:
        return
    glutPostRedisplay()

def reshape(width, height):
    h = float(width) / float(height)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(-1.0, 1.0, -h, h, 5.0, 3000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glutPostRedisplay()

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glEnable(GL_ALPHA_TEST)
    glEnable(GL_BLEND)
    glEnable(GL_COLOR_MATERIAL)

    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    amb = vec4(0.1, 0.1, 0.1, 0.0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, amb)
    pos = vec4(5.0, 5.0, 10.0, 0.0)
    glLightfv(GL_LIGHT0, GL_POSITION, pos)
        
    glHint(GL_POLYGON_SMOOTH_HINT,GL_NICEST)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST)

    glClearColor(.5,.5,.5,1.0)

def visible(vis):
    if vis == GLUT_VISIBLE:
        glutIdleFunc(idle)
    else:
        glutIdleFunc(None)

if __name__ == '__main__':
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

    glutInitWindowPosition(0, 0)
    glutInitWindowSize(800, 800)
    glutCreateWindow("glPerspectiveProjection")
    init()
    
    glutDisplayFunc(draw)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(key)
    glutSpecialFunc(special)
    glutVisibilityFunc(visible)

    glutMainLoop()