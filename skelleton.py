#from OpenGL.GL import *
from visual import *

# Scene
scene.autoscale = False
scene.range = (100,500,500)
scene.fullscreen = True
scene.title = 'NoppelBash'
scene.show_rendertime = True

# Room
room = frame()
wallR = box(frame=room, pos=( 100,  0,  0),size=(  1,100,100),color = color.red,
            material=materials.bricks)
wallL = box(frame=room, pos=(-100,  0,  0),size=(  1,100,100),color = color.red,
            material=materials.bricks)
wallT = box(frame=room, pos=(   0, 50,  0),size=(200,  1,100),color = color.gray(0.8),
            material=materials.marble)
wallB = box(frame=room, pos=(   0,-50,  0),size=(200,  1,100),color = color.orange,
            material=materials.wood)
wallF = box(frame=room, pos=(   0,  0,-50),size=(200,100,  1),color = color.red,
            material=materials.bricks)
#room.visible = False

# Boxing bag
boxingBag = frame()
bag = cylinder(frame=boxingBag, pos=(0,30,0), axis=(0,-50,0), radius=10,
               color=color.red, material=materials.rough)
rod = cylinder(frame=boxingBag, pos=(0,50,0), axis=(0,-30,0), radius=.5,
               color=color.gray(0.5), material=materials.blazed)
boxingBag.visible = False

# Dummie
texFace = materials.texture(data=materials.loadTGA("tex"),
                     mapping="rectangular", interpolate=False)

noppel = frame()
head = sphere(frame=noppel, pos=(0,20,0), radius=15, color=color.white,
               material=texFace,axis=(0,0,1))
torso = box(frame=noppel,pos=( 0,-10,0), length=20, height=30, width=12,
            color=color.red,material=materials.blazed)
armL = box(frame=noppel,pos=(-15,-10,0), length=5, height=20, width=5,
            color=color.red,material=materials.blazed)
armL.rotate(angle=radians(-25),axis=(0,0,1),origin=(-5,-10,0))
armR = box(frame=noppel,pos=(15,-10,0), length=5, height=20, width=5,
            color=color.red,material=materials.blazed)
armR.rotate(angle=radians(25),axis=(0,0,1),origin=(5,-10,0))
handL = sphere( frame=noppel, pos=(-19,-19,0), radius=4, color=(1,1,0),
               material=materials.marble)
handR = sphere( frame=noppel, pos=(19,-19,0), radius=4, color=(1,1,0),
               material=materials.marble)
legL = box(frame=noppel,pos=(0,-30,0), length=10, height=30, width=10,
            color=color.blue,material=materials.rough)
legL.rotate(angle=radians(-20),axis=(0,0,1),origin=(0,-10,0))
legR = box(frame=noppel,pos=(0,-30,0), length=10, height=30, width=10,
            color=color.blue,material=materials.rough)
legR.rotate(angle=radians( 20),axis=(0,0,1),origin=(0,-10,0))
footL = box(frame=noppel,pos=(-12,-47,5), length=10, height=6, width=15,
            color=color.green,material=materials.rough)
footR = box(frame=noppel,pos=( 12,-47,5), length=10, height=6, width=15,
            color=color.green,material=materials.rough)
#noppel.visible = False

# Lighting
light = frame()
scene.lights = []   # delete global lights
lampL = local_light(frame=light, pos=(-98,25, 0), color=color.gray(0.3))
lampR = local_light(frame=light, pos=( 98,25, 0), color=color.gray(0.3))
lampF = local_light(frame=light, pos=( 20,20,50), color=color.gray(0.2))

argZ=0.001
# Animation
while True:
    #rate(1000)

    if scene.mouse.clicked:
        m = scene.mouse.getclick()
        loc = m.project(normal=(0,0,1))
        print(loc)
        #sphere(pos=loc, color=color.cyan, radius=1)

    # Rotate around x
    #boxingBag.rotate(angle=radians( argX), axis=(1,0,0), origin=(0,50,0))
    #if(boxingBag.pos.z>40 or boxingBag.pos.z<-40):
    #    argX = -argX

    # Rotate around y
    #boxingBag.rotate(angle=radians( argY), axis=(0,1,0), origin=(0,50,0))
    #if(boxingBag.pos.x>40 or boxingBag.pos.x<-40):
    #    argY = -argY

    # Rotate around z
    boxingBag.rotate(angle=radians( argZ), axis=(0,0,1), origin=(0,50,0))
    if(boxingBag.pos.x>30 or boxingBag.pos.x<-30):
        argZ = -argZ
