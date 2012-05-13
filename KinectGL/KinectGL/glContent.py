#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# DONE: flaechennormale zu Kamera ausrichten
# DONE: Texturen, Befestigung Boxsack
# TODO: Kollisionskontrolle / Animation?
#       Quellen dazu:
#       http://nehe.gamedev.net/tutorial/collision_detection/17005/
#       http://www.peroxide.dk/download/tutorials/tut10/pxdtut10.html
#       http://www.realtimerendering.com/intersections.html
#       http://www.geometrictools.com/Documentation/MethodOfSeparatingAxes.pdf

# OpenGL und Toolkits laden
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

# timeing module fuer FPS-Berechnung
import time

# math module laden
import math

# IPL modul zum Laden von Texturen
from Image import open

# Typefed fuer Vektoren mit vier Komponenten
vec4 = GLfloat_4

# OpenGL Displaylists (vordefinierter Renderkontext)
wallList = 0
punchingBagList = 0

def drawCylinder( faces = 32, size = [1.0,1.0,1.0], pos = [0.0,0.0,0.0], angle = [0.0,0.0,0.0]):

    glPushMatrix()

    # Verschieben
    glTranslatef( pos[0], pos[1], pos[2])
    
    # Groesse anpassen
    glScalef( 0.5 * float(size[0]), 0.5 * float(size[1]), 0.5 * float(size[2]) )
    
    # Rotieren
    glRotatef( angle[0], 1.0, 0.0, 0.0)
    glRotatef( angle[1], 0.0, 1.0, 0.0)
    glRotatef( angle[2], 0.0, 0.0, 1.0)
    
    vect_x = vect_y = vect_z = 0
    glEnable(GL_NORMALIZE)

    glBegin(GL_QUAD_STRIP)
    for i in range(faces+1):
        vect_x = math.sin( float(i)/float(faces) * math.pi * 2.)
        vect_z = math.cos( float(i)/float(faces) * math.pi * 2.)
        vect_y = 1
 
        glTexCoord2f(float(i)/float(faces), 0)
        glNormal3f(vect_x, 0, vect_z)
        glVertex3f(vect_x, vect_y, vect_z)
 
        vect_y = -1
 
        glTexCoord2f(float(i)/float(faces), 1)
        glNormal3f(vect_x, 0, vect_z)
        glVertex3f(vect_x, vect_y, vect_z)
    glEnd()

    #Zeichnen der oberen Endkappe
    glBegin(GL_TRIANGLE_FAN)
    vect_y = 1
    glNormal3f(0, 1, 0)
    glTexCoord2f(0.5, 0.5)
    glVertex3f(0, 1, 0)
    for i in range(faces+1):
        vect_x = math.sin( float(i)/float(faces) * math.pi * 2.)
        vect_z = math.cos( float(i)/float(faces) * math.pi * 2.)
        glTexCoord2f(vect_x*0.5 + 0.5, vect_z*0.5 + 0.5)
        glVertex3f(vect_x,vect_y,vect_z)
    glEnd()
 
    #Zeichnen der unteren Endkappe
    glBegin(GL_TRIANGLE_FAN);
    vect_y = -1;
    glNormal3f(0, -1, 0);
    glTexCoord2f(0.5, 0.5);
    glVertex3f(0, -1, 0);
    i = faces
    while i >= 0:
        vect_x = math.sin( float(i)/float(faces) * math.pi * 2.)
        vect_z = math.cos( float(i)/float(faces) * math.pi * 2.)
        glTexCoord2f(0.5 - vect_x*0.5, vect_z*0.5 + 0.5)
        glVertex3f(vect_x, vect_y, vect_z)
        i -= 1
    glEnd()
 
    glDisable(GL_NORMALIZE)

    glPopMatrix()

def loadBindTex( tex_list):
    glEnable( GL_TEXTURE_2D)
    tex = glGenTextures( len( tex_list))

    for i, path in enumerate( tex_list):
        try:
            im = open(path)
            ix = im.size[0]
            iy = im.size[1]
            try:
                image = im.tostring("raw", "RGBA", 0, -1)
            except SystemError:
                image = im.tostring("raw", "RGBX", 0, -1)
            glBindTexture( GL_TEXTURE_2D, tex[i])
            glPixelStorei( GL_UNPACK_ALIGNMENT,1)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

            #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER  )
            #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER  )
            #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_BORDER  )

            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE) # GL_ADD, GL_MODULATE, GL_DECAL, GL_BLEND, GL_REPLACE, GL_COMBINE.
            glTexImage2D( GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
        except:
            print "Textur kann nicht erstellt werden"
            pass
    return tex

def createWallList(x = 80, y = 20, z = 250):
    # texture tutorial: http://pyopengl.sourceforge.net/documentation/openglcontext/images_and_textures.html
    # textures: http://www.photoshoptextures.com/
    img_files = ["wall.jpg","floor.jpg","ceiling.jpg"]

    glEnable( GL_TEXTURE_2D)
    tex = loadBindTex( img_files)

    list = glGenLists(1)
    glNewList( list, GL_COMPILE)

    glPushMatrix()

    glEnable( GL_NORMALIZE)
    glEnable( GL_TEXTURE_2D)

    glColor4f( 1.0, 1.0, 1.0, 1.0)

    # front
    glBindTexture( GL_TEXTURE_2D, tex[0])
    glBegin(GL_QUADS)
    glTexCoord2d(0.0,1.0); glNormal3f( 0.0, 0.0,-1.0); glVertex3f(-x, y, z)
    glTexCoord2d(0.0,0.0); glNormal3f( 0.0, 0.0,-1.0); glVertex3f(-x,-y, z)
    glTexCoord2d(1.0,0.0); glNormal3f( 0.0, 0.0,-1.0); glVertex3f( x,-y, z)
    glTexCoord2d(1.0,1.0); glNormal3f( 0.0, 0.0,-1.0); glVertex3f( x, y, z)
    glEnd()
    # back
    #glBindTexture( GL_TEXTURE_2D, tex[0])
    glBegin(GL_QUADS)
    glTexCoord2d(0.0,1.0); glNormal3f( 0.0, 0.0, 1.0); glVertex3f(-x, y,-z)
    glTexCoord2d(0.0,0.0); glNormal3f( 0.0, 0.0, 1.0); glVertex3f(-x,-y,-z)
    glTexCoord2d(1.0,0.0); glNormal3f( 0.0, 0.0, 1.0); glVertex3f( x,-y,-z)
    glTexCoord2d(1.0,1.0); glNormal3f( 0.0, 0.0, 1.0); glVertex3f( x, y,-z)
    glEnd()
    # left
    #glBindTexture( GL_TEXTURE_2D, tex[0])
    glBegin(GL_QUADS)
    glTexCoord2d(0.0,1.0); glNormal3f( 1.0, 0.0, 0.0); glVertex3f(-x, y, z)
    glTexCoord2d(0.0,0.0); glNormal3f( 1.0, 0.0, 0.0); glVertex3f(-x,-y, z)
    glTexCoord2d(1.0,0.0); glNormal3f( 1.0, 0.0, 0.0); glVertex3f(-x,-y,-z)
    glTexCoord2d(1.0,1.0); glNormal3f( 1.0, 0.0, 0.0); glVertex3f(-x, y,-z)
    glEnd()
    # right
    #glBindTexture( GL_TEXTURE_2D, tex[0])
    glBegin(GL_QUADS)
    glTexCoord2d(0.0,1.0); glNormal3f(-1.0, 0.0, 0.0); glVertex3f( x, y, z)
    glTexCoord2d(0.0,0.0); glNormal3f(-1.0, 0.0, 0.0); glVertex3f( x,-y, z)
    glTexCoord2d(1.0,0.0); glNormal3f(-1.0, 0.0, 0.0); glVertex3f( x,-y,-z)
    glTexCoord2d(1.0,1.0); glNormal3f(-1.0, 0.0, 0.0); glVertex3f( x, y,-z)
    glEnd()
    # top
    glBindTexture( GL_TEXTURE_2D, tex[2])
    glBegin(GL_QUADS)
    glTexCoord2d(0.0,1.0); glNormal3f( 0.0,-1.0, 0.0); glVertex3f(-x, y, z)
    glTexCoord2d(0.0,0.0); glNormal3f( 0.0,-1.0, 0.0); glVertex3f(-x, y,-z)
    glTexCoord2d(1.0,0.0); glNormal3f( 0.0,-1.0, 0.0); glVertex3f( x, y,-z)
    glTexCoord2d(1.0,1.0); glNormal3f( 0.0,-1.0, 0.0); glVertex3f( x, y, z)
    glEnd()
    # bottom
    glBindTexture( GL_TEXTURE_2D, tex[1])
    glBegin(GL_QUADS)
    glTexCoord2d(0.0,1.0); glNormal3f( 0.0, 1.0, 0.0); glVertex3f(-x,-y, z)
    glTexCoord2d(0.0,0.0); glNormal3f( 0.0, 1.0, 0.0); glVertex3f(-x,-y,-z)
    glTexCoord2d(1.0,0.0); glNormal3f( 0.0, 1.0, 0.0); glVertex3f( x,-y,-z)
    glTexCoord2d(1.0,1.0); glNormal3f( 0.0, 1.0, 0.0); glVertex3f( x,-y, z)
    glEnd()

    glPopMatrix()

    glDisable( GL_TEXTURE_2D)
    glDisable( GL_NORMALIZE)

    glEndList()
    return list

def createPunchingBagList():
    img_files = ["leather.jpg","rope.jpg"]

    glEnable( GL_TEXTURE_2D)
    tex = loadBindTex( img_files)

    list = glGenLists(1)
    glNewList( list, GL_COMPILE)

    glEnable( GL_TEXTURE_2D)
    glPushMatrix()

    glBindTexture( GL_TEXTURE_2D, tex[0])
    glColor4f(0.2, 0.2, 0.2, 1.0)   
    drawCylinder( 128, [8, 20,8])    
    
    glBindTexture( GL_TEXTURE_2D, tex[1])
    glColor4f(1.0, 1.0, 1.0, 1.0)   
    drawCylinder( 128, [ 0.4, 20, 0.4], [ 0, 10, 0])   

    glPopMatrix()

    glEndList()
    return list

# OpenGL initialisieren
def initGL():
    global wallList, punchingBagList
    # Tiefenpuffer aktivieren
    glEnable(GL_DEPTH_TEST)

    # Flaechennormale aktivieren
    #glEnable(GL_NORMALIZE)

    # Alphatest aktivieren
    #glEnable(GL_ALPHA_TEST)

    # Blending aktivieren (neue Bilddaten mit alten Verrechnen)
    #glEnable(GL_BLEND)

    # Kantenglaettung
    glHint(GL_POLYGON_SMOOTH_HINT,GL_NICEST)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST)

    # Position und Farbe der Lichtquelle setzen
    glLightfv(GL_LIGHT0, GL_AMBIENT, vec4(0.0, 0.0, 0.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec4(1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec4(1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_POSITION, vec4(1.0, 1.0, 0.0, 1.0))
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, vec4(0.2, 0.2, 0.2, 1.0) )

    # Beleuchtung aktivieren
    glEnable(GL_LIGHTING)

    # Eine Lichtquelle 'einschalten'
    glEnable(GL_LIGHT0) 

    # Materialeigenschaften aktivieren
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv( GL_FRONT_AND_BACK, GL_SPECULAR, vec4(1.0, 1.0, 1.0, 1.0))
    glMaterialfv( GL_FRONT_AND_BACK, GL_EMISSION, vec4(0.0, 0.0, 0.0, 1.0))

    # Hintergrundfarbe
    glClearColor(0.,0.,0.,1.0)

    # Erstelle display lists
    wallList = createWallList()
    punchingBagList = createPunchingBagList()

# String rendern und ausgeben
def renderStr( x, y, string, r = 0.2, g = 0.8, b = 0.2, font = GLUT_BITMAP_HELVETICA_10):
    # Wechsel zu orthogonaler (zweidimensionaler) Ansicht
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0.0, glutGet(GLUT_WINDOW_WIDTH), 0.0, glutGet(GLUT_WINDOW_HEIGHT))

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    lightSet = glGetBoolean(GL_LIGHTING)
    if lightSet:
        glDisable(GL_LIGHTING)
    
    # Tiefenpuffer deaktivieren
    depthSet = glGetBoolean(GL_DEPTH_TEST)
    if depthSet:
        glDisable(GL_DEPTH_TEST)

    # Setze Farbe
    glColor3f( r, g, b)

    # Setze Position
    glRasterPos2i(x, y)

    # Render jeden Buchstaben einzeln
    for c in string:
        glutBitmapCharacter( font, ord(c) )

    # Stelle alten Zustand wieder her
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    if lightSet:
        glEnable(GL_LIGHTING)

    # Tiefenpuffer aktivieren
    if depthSet:
        glEnable(GL_DEPTH_TEST)

# Framerate berechnen
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

ani_angle = 0.
ani_inc = 0.25
def renderScene( center):
    global wallList, punchingBagList
    global ani_angle, ani_inc

    # Boxsack rendern
    glPushMatrix()
    glTranslatef( center[0], center[1], center[2])

    glTranslatef( 0.0, 20.0,0.0)
    glRotatef( ani_angle, 0.0, 0.0, 1.0)
    ani_angle += ani_inc
    if ani_angle > 20. or ani_angle < -20.:
        ani_inc *= -1.
    glTranslatef( 0.0, -20.0,0.0)

    glColor4f(1.0, 0.55, 0.0,1.0)
    glCallList( punchingBagList)
    glPopMatrix()

    # Raum rendern
    glCallList( wallList)