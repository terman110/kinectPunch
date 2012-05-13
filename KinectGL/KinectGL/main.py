#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

PROGRAM_TITLE = "Perspective Boxing"

# Benoetigte Module (alle 32Bit, unabhaengig von Betriebssystem):
# Python 2.7:                       http://python.org/download/releases/2.7.3/
# setuptools:                       http://pypi.python.org/pypi/setuptools
# Windows: pywin32:                 http://sourceforge.net/projects/pywin32/
# NumPy:                            http://numpy.scipy.org/
# pygame:                           http://www.pygame.org/download.shtml
# PyOpenGL 3.x:                     http://pyopengl.sourceforge.net/
# Python Imaging Library (PIL):     http://www.pythonware.com/products/pil/
# PyKinect (startet auch ohne):     https://pytools.codeplex.com/wikipage?title=PyKinect
# fuer PyKinect:
#   Visual Studio 2010, z.B.:       https://www.microsoft.com/visualstudio/en-us/products/2010-editions/visual-cpp-express  (VISUAL C++ 2010 EXPRESS)
#   KinectSDK (32 Bit):             http://kinectforwindows.org/

# Bibliotheken laden
from numpy import *
import sys
import itertools
import ctypes
import thread

# pyGame laden
import pygame
from pygame.locals import *

# pyKinect laden
try:
    import pykinect
    from pykinect import nui
    from pykinect.nui import JointId
except:
    print "pyKinect konnte nicht geladen werden"
    pass

# OpenGL Funktionen und Bibliotheken laden
from glContent import *

# Fenstergroess (GLUT)
WIN_SIZE = [ 1024, 768]

# Groesse des Kinect-Tiefenpuffers
DEPTH_SIZE = ( 320, 240)

# Intensitaet der Perspektivenmanipulation
cam_pos_multiplier = 20

# Cameraposition
cam = [0.0, 0.0, -100.0]

# Kinect verfuegbar
kinect_available = True

# Schalter fuer Hilfsmenue
help_menu = False

# Hilfsmenue
help = ( PROGRAM_TITLE,
         "",
         "Tastaturbelegung:",
         "  \"h\"     : Hilfe ein/ ausschalten",
         "  \"Hoch\"  : Kinect stärker neigen",
         "  \"Runter\": Kinect schwächer neigen",
         "  \"q\"     : Kameraposition weiter vom Zentrum entfernen",
         "  \"e\"     : Kameraposition weiter zum Zentrum führen",
         "  \"f\"     : Vollbildmodus umschalten",
         "  \"ESC\"   : Programm beenden" )

#############################################################
#                                                           #
#   OpenGL und GLUT                                         # 
#                                                           #
#############################################################

# Berechnet neue Kamerakoordinaten aus Kinect-Tiefenpuffer und speichert sie in cam
def updateCamFromKinectEvent():
    global DEPTH_SIZE, WIN_SIZE, cam_pos_multiplier, cam, kinect_available

    # Wenn kein Kinect-Event wartet, zurückgeben!
    if not kinect_available or not pygame.event.peek:
        return

    # pyGame-Events nach Kinect-Events durchsuchen
    events = pygame.event.get()
    for i, e in enumerate(events):

        # Kinect-Eventgefunden
        if e.type == KINECTEVENT:

            # Skeletdaten laden
            # Alle Skeletdaten verarbeiten
            for index, data in enumerate(e.skeletons):

                # Poisition des Kopfs in Fensterkoordinaten bestimmen
                HeadPos = skeleton_to_depth_image(data.SkeletonPositions[JointId.Head], DEPTH_SIZE[0], DEPTH_SIZE[1])

                # Fensterdaten in realtive OpenGl-Koordinaten der Kameraposition umrechnen
                if(HeadPos[0] != 0 or HeadPos[1] != 0):
                    cam[0] = ( HeadPos[0] / DEPTH_SIZE[0] * 2. - 1. ) * cam_pos_multiplier
                    cam[1] = ( HeadPos[1] / DEPTH_SIZE[1] * 2. - 1. ) * cam_pos_multiplier * float(WIN_SIZE[1]) / float(WIN_SIZE[0])

# GLUT-Callbackfunktion. Grafik rendern
def draw():
    global cam, help_menu, help

    # Skybox coordinates
    center = (0.0, 0.0, 100.0)

    # Matrizen des Modellraums laden
    glMatrixMode(GL_MODELVIEW)

    # Farb(pixel)puffer und Tiefenpuffer (OpenGL!) loeschen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Neu Kamerakoordinaten aus Kinect-Tiefenpuffer berechnen und in cam speichern
    updateCamFromKinectEvent()

    # Neue perspektivische Matrix berechnen und Matrix anwenden
    # http://pyopengl.sourceforge.net/documentation/manual/gluLookAt.3G.html
    glLoadIdentity()
    gluLookAt( -cam[0], cam[1], cam[2], center[0], center[1], center[2], 0, 1, 0)

    # Szene rendern
    renderScene( center)

    # Hilfe ausgeben
    if help_menu:
        offset = 17
        length = len(help)
        for index, string in enumerate(help):
            renderStr( 50, (length  + 4 )*offset-(index+1)*offset, string, 1.0, 1.0, 1.0, GLUT_BITMAP_9_BY_15 )

    renderStr( 10, 10, 'Kameraposition ( {}, {}, {} )'.format( cam[0], cam[1], cam[2] ), .2, .8, .2, GLUT_BITMAP_8_BY_13)
    renderStr( 10, 25, '{} FPS'.format( int(framerate()) ), 1.0, 1.0, 1.0, GLUT_BITMAP_9_BY_15 )

    glutSwapBuffers()

# GLUT-Callbackfunktion. Wird im Leerlauf aufgerufen und fordert zum rendern auf 
def idle():
    # GLUT zum rendern auffordern (Display-Callback laden)
    glutPostRedisplay()
    
isFS = 0    # Ist GLUT im Vollbildmodus?
# GLUT-Callbackfunktion. Taste gedruekt
def key(k, x, y):
    global cam, isFS, help_menu, WIN_SIZE

    # w: Kamera nach rechts
    if k == 'd':
        cam[0] += 0.5

    # s: Kamera nach links
    elif k == 'a':
        cam[0] -= 0.5

    # w: Kamera nach oben
    elif k == 'w':
        cam[1] += 0.5

    # s: Kamera nach unten
    elif k == 's':
        cam[1] -= 0.5

    # q: Kamera weiter vom Zentrum entfernen
    elif k == 'q':
        cam[2] -= 0.5

    # e: Kamera weiter zum Zentrum fuehren
    elif k == 'e':
        cam[2] += 0.5

    # q: Kamera weiter vom Zentrum entfernen
    if k == 'q':
        cam[2] -= 0.5

    # e: Kamera weiter zum Zentrum fuehren
    elif k == 'e':
        cam[2] += 0.5

    # f: Vollbildmodus umschalten
    elif k == 'f':
        if isFS == 0:
            glutFullScreen()
            isFS = 1
        else:
            glutReshapeWindow( WIN_SIZE[0], WIN_SIZE[1])
            isFS = 0

    # h: Hilfe einblenden
    elif k == 'h':
        if help_menu == True:
            help_menu = False
        else:
            help_menu = True

    # ESC: Programm beenden
    elif ord(k) == 27: # Escape
        sys.exit(0)
    else:
        return

    # GLUT zum rendern auffordern (Display-Callback laden)
    glutPostRedisplay()

# GLUT-Callbackfunktion. Sondertaste gedruekt
def special(k, x, y):  
  
    # Pfeielobentaste: Kinect staerker neigen
    if k == GLUT_KEY_UP:
        try:
            kinect.camera.elevation_angle = kinect.camera.elevation_angle + 2
        except:
            print "Kinect nicht verfügbar?!"
            pass

    # Pfeieluntentaste: Kinect schwaecher neigen
    elif k == GLUT_KEY_DOWN:
        try:
            kinect.camera.elevation_angle = kinect.camera.elevation_angle - 2
        except:
            print "Kinect nicht verfügbar?!"
            pass
    else:
        return

    # GLUT zum rendern auffordern (Display-Callback laden)
    glutPostRedisplay()

# GLUT-Callbackfunktion. Fensterdimensionen haben sich geaendert.
def reshape(width, height):
    global WIN_SIZE
    
    # Neue Fenstergroesse festlegen
    WIN_SIZE[0] = width
    WIN_SIZE[1] = height

    # Verhaeltnis uwischen Hoehe und Breite
    h = float(height)/ float(width)

    # Neuer Viewport
    glViewport(0, 0, width, height)

    # Projektionsmatrix manipulieren
    glMatrixMode(GL_PROJECTION)
    # Einheitsmatrix laden
    glLoadIdentity()
        
    # Neue Frustums-Matrix berechnen und uebergeben
    glFrustum(-1.0, 1.0, -h, h, 5.0, 3000.0)

    # Moderlierungsmatrix manipulieren
    glMatrixMode(GL_MODELVIEW)
    # Einheitsmatrix laden
    glLoadIdentity()
    
    # GLUT zum rendern auffordern (Display-Callback laden)
    glutPostRedisplay()

# GLUT-Callbackfunktion. Test ob Fenster sichtbar ist.
def visible(vis):
    if vis == GLUT_VISIBLE:
        glutIdleFunc(idle)
    else:
        glutIdleFunc(None)

# GLUT (OpenGL Utility Toolkit) initialisieren 
def initGLUT():
    global sys

    # GLUT starten
    glutInit(sys.argv)

    # Anzeigemodus definieren
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

    # Fensterposition
    sw = glutGet( GLUT_SCREEN_WIDTH) - WIN_SIZE[0]
    sh = glutGet( GLUT_SCREEN_HEIGHT) - WIN_SIZE[1]
    glutInitWindowPosition( sw/2, sh/2)

    # Fenstergroesse
    glutInitWindowSize(WIN_SIZE[0], WIN_SIZE[1])

    # Fenster erstellen und Titel zuweisen
    glutCreateWindow( PROGRAM_TITLE)

    # Callbackfunktionen festlegen
    glutDisplayFunc(draw)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(key)
    glutSpecialFunc(special)
    glutVisibilityFunc(visible)
	

#############################################################
#                                                           #
#   pyGame und pyKinect                                     # 
#                                                           #
#############################################################

# pyGameEvent fuer neue Kinectdaten
KINECTEVENT = pygame.USEREVENT

# Typedef zut generierung der Tiefeninformationen aus Skelettdaten
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

# Wandle Bildschirmkoordinaten um
def surface_to_array(surface):
   buffer_interface = surface.get_buffer()
   address = ctypes.c_void_p()
   size = Py_ssize_t()
   _PyObject_AsWriteBuffer(buffer_interface,
                          ctypes.byref(address), ctypes.byref(size))
   bytes = (ctypes.c_byte * size.value).from_address(address.value)
   bytes.object = buffer_interface
   return bytes

# Callback-Funktion. Wird aufgerufen, wenn neuer Tiefenpuffer von Kinect verfuegbar ist
def depth_frame_ready(frame):
    # Im Thread ...
    with screen_lock:
        # Bildschirmkoordinaten uebersetzen
        address = surface_to_array(screen)
        ctypes.memmove(address, frame.image.bits, len(address))
        del address
        # Skeletdaten zur Verfuegung stellen
        skeleleton_data = skeletons
        # pyGame-Fenster refreshen
        pygame.display.update()   

# Callback-Funktion. Wird aufgerufen, wenn neuer Frame von Kinect verfuegbar ist
def post_frame(frame):
        try:
            # Skeletdaten an KINECTEVENT uebergeben
            pygame.event.post(pygame.event.Event(KINECTEVENT, skeletons = frame.SkeletonData))
        except:
            #print(" event queue full ")
            pass

#############################################################
#                                                           #
#   Main                                                    # 
#                                                           #
#############################################################

if __name__ == '__main__':
        
    for h in help:
        print h    

    # GLUT initialisieren
    initGLUT()

    # OpenGL initialisieren
    initGL()
    
    # Thread fuer die Kinect-Datenerfassung
    screen_lock = thread.allocate()
    
    # Initialisiere pyGame-Fenster fuer den Kinect Tiefenpuffer
    pygame.init()
    pygame.display.set_caption = PROGRAM_TITLE
    screen = pygame.display.set_mode(DEPTH_SIZE,0,16)
    pygame.display.iconify = True
    skeletons = None

    try:
        # Initialisiere Kinect (NUI-Runtime)
        kinect = nui.Runtime()

        # Aktiviere Skeletdaten
        kinect.skeleton_engine.enabled = True

        # Weise Callbackfunction post_frame zu, die bei jedem neuen Frame aufgerufen wird
        kinect.skeleton_frame_ready += post_frame

        # Weise Callbackfunction depth_frame_ready zu, die aufgeruden wird wenn neues Bild des Tiefenpuffers verfuegbar ist
        kinect.depth_frame_ready += depth_frame_ready    

        # Starte Tiefenpuffer-Stream
        kinect.depth_stream.open(nui.ImageStreamType.Depth, 2, nui.ImageResolution.Resolution320x240, nui.ImageType.Depth)
    except:
        # Fange exception falls Kinect nicht verfuegbar ist
        kinect_available = False
        print "#  FEHLER: Kinect kann nicht gefunden bzw. die NUI-Runtime nicht initialisiert werden."
        pass

    # Starte die "GLUT-Schleife"
    glutMainLoop()
