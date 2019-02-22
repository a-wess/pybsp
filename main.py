import struct
import moderngl as ModernGL
import pyglet
from renderer import Renderer
from pyglet.window import key
from camera import Camera
from pathlib import Path
from bsp import BSP
import mymath as m
import itertools
import sys

wnd = pyglet.window.Window(width = 640, height = 480)
wnd.set_exclusive_mouse(True)
keys = key.KeyStateHandler()
wnd.push_handlers(keys)

ctx = ModernGL.create_context()
ctx.enable(ModernGL.DEPTH_TEST)
ctx.wireframe = True

pos = (812.0, 64.0, -856.0)
forward = m.cross(pos, (0.0, 1.0, 0.0))
#camera = Camera((241.0, 82.0, -2340.0), (533.0, 80.0, -2149.0), (90, 1.0, 1500.0))
camera = Camera(pos, forward, (90, 1.0, 1500.0))
bsp = BSP('q3dm1.bsp')
bsp.preload(ctx)
#bsp.set_camera((241.0, 2340.0, 82.0))
renderer = Renderer(bsp, camera, ctx)


#@wnd.event
def draw():
	ctx.clear(0.9, 0.9, 0.9)
	renderer.draw()

def camera_movement():
	if keys[key.W]:
		camera.move(0)
	if keys[key.A]:
		camera.move(3)
	if keys[key.D]:
		camera.move(2)
	if keys[key.S]:
		camera.move(1)

@wnd.event
def on_mouse_motion(x, y, dx, dy):
	camera.mouse(dx, dy)

def main_loop(delta):
	camera.delta = delta
	camera_movement()
	bsp.set_camera((camera.position[0], -camera.position[2], camera.position[1]))
	renderer.prepare_buffer()
	draw()

pyglet.clock.schedule_interval(main_loop, 1.0/60.0)
pyglet.app.run()

