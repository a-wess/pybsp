import struct
import moderngl as ModernGL
from pathlib import Path

class Renderer():
	def __init__(self, bsp, camera, context):
		self.bsp = bsp
		self.camera = camera
		self.context = context
		self.curr_leaf = None
		self.vaos = None
		self.faces = None
		vert = Path('shaders/basic.vert').read_text()
		frag = Path('shaders/basic.frag').read_text()
		self.prog = self.context.program(
			vertex_shader = vert,
			fragment_shader = frag
		)
		self.view = self.prog['view']
		self.proj = self.prog['proj']
		self.prog['lightmap'].value = 0
		self.proj.value = self.camera.get_proj()


	def prepare_buffer(self):
		leaf = self.bsp.find_leaf()
		if not self.curr_leaf or leaf.cluster != self.curr_leaf.cluster:
			#print("Update")
			self.curr_leaf = leaf
			#print(self.curr_leaf.cluster)
			visible_set = self.bsp.find_visible(self.curr_leaf)
			self.faces = self.bsp.get_faces(visible_set)
			content = [(self.bsp.VBO, '3f 2f 4f', 'in_vert', 'in_lm', 'in_color')]
			#print(self.bsp.VBO.size)
			self.vaos = []
			for face in self.faces:
				if face.type == 1 or face.type == 3:
					mvertices = self.bsp.mvertices[face.meshvert : face.meshvert + face.n_meshverts]
					mvertices = [face.vertex + x for x in mvertices]
					index_buffer = self.context.buffer(struct.pack('%si' % len(mvertices), *mvertices))
					VAO = self.context.vertex_array(self.prog, content, index_buffer)
					self.vaos.append(VAO)


	def draw(self):
		self.view.value = self.camera.get_view()
		for i in range(len(self.vaos)):
			face = self.faces[i]
			if True: #face.lm_index > -1:
				self.bsp.lightmaps[face.lm_index].use(0)
				self.vaos[i].render(ModernGL.TRIANGLES)
		
