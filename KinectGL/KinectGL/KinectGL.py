#!/usr/bin/env python2.3

import sys, time 
from numpy import *
import itertools
import ctypes
import thread

import pygame
from pygame.color import THECOLORS
from pygame.locals import *

try:
    # For OpenGL-ctypes
    from OpenGL import platform
    gl = platform.OpenGL
except ImportError:
    try:
        # For PyOpenGL
        gl = cdll.LoadLibrary('libGL.so')
    except OSError:
        # Load for Mac
        from ctypes.util import find_library
        # finds the absolute path to the framework
        path = find_library('OpenGL')
        gl = cdll.LoadLibrary(path)
 
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import pykinect
from pykinect import nui
from pykinect.nui import JointId

max_val = 20
WinW = 1024
WinH = 768
KINECTEVENT = pygame.USEREVENT
DEPTH_SIZE = 320,240
VIDEO_SIZE = 640,480
pygame.init()

skeleton_to_depth_image = nui.SkeletonEngine.skeleton_to_depth_image

# recipe to get address of surface: http://archives.seul.org/pygame/users/Apr-2008/msg00218.html
if hasattr(ctypes.pythonapi, 'Py_InitModule4'):
   Py_ssize_t = ctypes.c_int
elif hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
   Py_ssize_t = ctypes.c_int64
else:
   raise TypeError("Cannot determine type of Py_ssize_t")

_PyObject_AsWriteBuffer = ctypes.pythonapi.PyObject_AsWriteBuffer
_PyObject_AsWriteBuffer.restype = ctypes.c_int
_PyObject_AsWriteBuffer.argtypes = [ctypes.py_object,
                                  ctypes.POINTER(ctypes.c_void_p),
                                  ctypes.POINTER(Py_ssize_t)]

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
    global skel
    global target_x, target_y, target_z

    events = pygame.event.get()
    for i, e in enumerate(events):
        if e.type == KINECTEVENT:
            skeletons = e.skeletons
            for index, data in enumerate(skeletons):
                #if index == 0:
                    HeadPos = skeleton_to_depth_image(data.SkeletonPositions[JointId.Head], DEPTH_SIZE[0], DEPTH_SIZE[1]) 
                    if(HeadPos[0] != 0 and HeadPos[1] != 0):
                        frac = float(WinH) / float(WinW)
                        target_x = ( HeadPos[0] / DEPTH_SIZE[0] * 2. - 1. ) * max_val
                        target_y = ( HeadPos[1] / DEPTH_SIZE[1] * 2. - 1. ) * max_val * frac

    # Skybox coordinates
    x = 30
    y = 20
    z = 800
    tea_pos = (0.0, 0.0, float(z)/4.0)

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
    glutPostRedisplay()
    
isFS = 0
def key(k, x, y):
    global view_rotz
    global target_x, target_y, target_z
    global isFS

    if k == 'z':
        view_rotz += 5.0
    elif k == 'Z':
        view_rotz -= 5.0
    elif k == 'q':
        target_z -= 0.1
    elif k == 'e':
        target_z += 0.1
    elif k == 'f':
        if isFS == 0:
            glutFullScreen()
            isFS = 1
        else:
            glutReshapeWindow(800,800)
            isFS = 0
    elif ord(k) == 27: # Escape
        sys.exit(0)
    else:
        return
    glutPostRedisplay()

def special(k, x, y):
    global view_rotx, view_roty, view_rotz
    
    if k == GLUT_KEY_UP:
        kinect.camera.elevation_angle = kinect.camera.elevation_angle + 2
    elif k == GLUT_KEY_DOWN:
        kinect.camera.elevation_angle = kinect.camera.elevation_angle - 2
    elif k == GLUT_KEY_LEFT:
        view_roty += 5.0
    elif k == GLUT_KEY_RIGHT:
        view_roty -= 5.0
    else:
        return
    glutPostRedisplay()

def reshape(width, height):
    global WinW, WinH
    WinW = width
    WinH = height
    h = float(height)/ float(width)

    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(-1.0, 1.0, -h, h, 5.0, 3000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glutPostRedisplay()

def visible(vis):
    if vis == GLUT_VISIBLE:
        glutIdleFunc(idle)
    else:
        glutIdleFunc(None)

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

def surface_to_array(surface):
   buffer_interface = surface.get_buffer()
   address = ctypes.c_void_p()
   size = Py_ssize_t()
   _PyObject_AsWriteBuffer(buffer_interface,
                          ctypes.byref(address), ctypes.byref(size))
   bytes = (ctypes.c_byte * size.value).from_address(address.value)
   bytes.object = buffer_interface
   return bytes

def depth_frame_ready(frame):
    with screen_lock:
        address = surface_to_array(screen)
        ctypes.memmove(address, frame.image.bits, len(address))
        del address
        skel = skeletons
        pygame.display.update()   

def post_frame(frame):
        try:
            pygame.event.post(pygame.event.Event(KINECTEVENT, skeletons = frame.SkeletonData))
        except:
            #print(" event queue full ")
            pass

if __name__ == '__main__':
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

    glutInitWindowPosition(0, 0)
    glutInitWindowSize(WinW, WinH)
    glutCreateWindow("glPerspectiveProjection")
    init()
    
    glutDisplayFunc(draw)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(key)
    glutSpecialFunc(special)
    glutVisibilityFunc(visible)

    screen_lock = thread.allocate()
    
    screen = pygame.display.set_mode(DEPTH_SIZE,0,16)
    pygame.display.iconify = True
    skeletons = None
    kinect = nui.Runtime()
    kinect.skeleton_engine.enabled = True
    kinect.skeleton_frame_ready += post_frame
    kinect.depth_frame_ready += depth_frame_ready    
    kinect.depth_stream.open(nui.ImageStreamType.Depth, 2, nui.ImageResolution.Resolution320x240, nui.ImageType.Depth)

    glutMainLoop()