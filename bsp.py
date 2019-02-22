from bsp_loader import BSP_loader
from namedlist import namedlist
import mymath

camera = namedlist('camera', ['position'])

class BSP():
	def __init__(self, path):
		loader = BSP_loader(path)
		self._loader = loader
		self.entities = loader.entities
		self.textures = loader.textures
		self.planes = loader.planes
		self.nodes = loader.nodes
		self.leafs = loader.leafs
		self.leaffaces = loader.leaffaces
		self.leafbrushes = loader.leafbrushes
		self.models = loader.models
		self.brushes = loader.brushes
		self.brushsides = loader.brushsides
		self.vertices = loader.vertices
		self.mvertices = loader.mvertices
		self.effects = loader.effects
		self.faces = loader.faces
		self.lightmaps = loader.lightmaps
		self.lightvol = loader.lightvol
		self.visdata = loader.visdata
		self.camera = camera((0.0, 0.0, 0.0))
	def find_leaf(self):
		index = 0
		while index > -1:
			node = self.nodes[index]
			plane = self.planes[node.plane]
			distance = mymath.dot(plane.normal, self.camera.position) - plane.dist
			if distance >= 0:
				index = node.children[0]
			else:
				index = node.children[1]
		return self.leafs[-(index + 1)]

	def find_visible(self, leafA):
		clusterA = leafA.cluster
		leaves = []
		for leafB in self.leafs:
			clusterB = leafB.cluster
			if clusterB > 0:
				bits = ord(self.visdata.vecs[clusterB * self.visdata.sz_vecs + clusterA//8])
				if bits >> clusterA % 8 & 1:
					leaves.append(leafB)
		return leaves

	def get_faces(self, leaves):
		face_indexes = set()
		faces = []
		for leaf in leaves:
			for f_index in self.leaffaces[leaf.leafface : leaf.leafface + leaf.n_leaffaces]:
				if f_index not in face_indexes:
					face_indexes.add(f_index)
					faces.append(self.faces[f_index])
		return faces

	def set_camera(self, vec3):
		self.camera.position = vec3

	def preload(self, context):
		self.VBO = self._loader.preload_vertices(context)
		self.lightmaps = self._loader.preload_lightmaps(context)
		self._loader = None
	def get_random_position(self):
		


