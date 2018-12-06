import struct
import moderngl as ModernGL
import pyglet
from pyglet.window import key
from camera import Camera
from pathlib import Path
from bsp import BSP
import itertools
import sys

wnd = pyglet.window.Window(width = 640, height = 480)
wnd.set_exclusive_mouse(True)
keys = key.KeyStateHandler()
wnd.push_handlers(keys)

ctx = ModernGL.create_context()
ctx.enable(ModernGL.DEPTH_TEST)
#ctx.wireframe = True

vert = Path('shaders/basic.vert').read_text()
frag = Path('shaders/basic.frag').read_text()

prog = ctx.program(
	vertex_shader = vert,
	fragment_shader = frag
)
print(prog._members)

camera = Camera((241.0, 82.0, -2340.0), (533.0, 80.0, -2149.0), (90, 1.0, 2000.0))

view = prog['view']
proj = prog['proj']
prog['lightmap'].value = 0
view.value = camera.get_view()
proj.value = camera.get_proj()

bsp = BSP('q3dm1.bsp')
bsp.preload(ctx)
bsp.set_camera((241.0, 2340.0, 82.0))
l = bsp.find_leaf()
s = bsp.find_visible(l)
faces = bsp.get_faces(s)

content = [(bsp.VBO, '3f 2f 4f', 'in_vert', 'in_lm', 'in_color')]
vaos = []
for face in faces:
	if face.type == 1 or face.type == 3:
		mvertices = bsp.mvertices[face.meshvert : face.meshvert + face.n_meshverts]
		mvertices = [face.vertex + x for x in mvertices]
		index_buffer = ctx.buffer(struct.pack('%si' % len(mvertices), *mvertices))
		VAO = ctx.vertex_array(prog, content, index_buffer)
		vaos.append(VAO)
	#elif face.type == 2:
		

#@wnd.event
def draw():
	view.value = camera.get_view()
	ctx.clear(0.9, 0.9, 0.9)
	for i in range(len(vaos)):
		face = faces[i]
		if True: #face.lm_index > -1:
			bsp.lightmaps[face.lm_index].use(0)
			vaos[i].render(ModernGL.TRIANGLES)

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
	draw()

pyglet.clock.schedule_interval(main_loop, 1.0/60.0)
pyglet.app.run()

