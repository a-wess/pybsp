from namedlist import namedlist
import struct
import numpy as np

INT_SIZE = 4
FLOAT_SIZE = 4

direntry = namedlist('direntry', ['offset', 'length'])
DIRENTRY = ['int', 'int']

texture = namedlist('texture', ['tex', 'flags', 'contents']) # c64, int, int
TEXTURE = ['str64', 'int', 'int']

plane = namedlist('plane', ['normal', 'dist']) # float[3] float
PLANE = ['3float', 'float']

node = namedlist('node', ['plane', 'children', 'mins', 'maxs'])
NODE = ['int', '2int', '3int', '3int']

leaf = namedlist('leaf', ['cluster','area','mins','maxs','leafface','n_leaffaces','leafbrush','n_leafbrushes'])
LEAF = ['int', 'int', '3int', '3int', 'int', 'int', 'int', 'int']

model = namedlist('model', ['mins', 'maxs', 'face', 'n_faces', 'brush', 'n_brushes'])
MODEL = ['3float', '3float', 'int', 'int', 'int', 'int']

brush = namedlist('brush', ['brushside', 'n_brushsides', 'texture'])
BRUSH = ['int', 'int', 'int']

brushside = namedlist('brushside', ['plane', 'texture'])
BRUSHSIDE = ['int', 'int']

vertex = namedlist('vertex', ['position', 'texcoord', 'normal', 'color'])
VERTEX = ['3float', 'mat2x2_float', '3float', '4ubyte']

effect = namedlist('effect', ['name', 'brush', 'unknown'])
EFFECT = ['str64', 'int', 'int']

face = namedlist('face', ['texture', 'effect', 'type',
						   'vertex', 'n_vertexes',
						   'meshvert', 'n_meshverts',
						   'lm_index', 'lm_start',
						   'lm_size', 'lm_origin',
						   'lm_vecs', 'normal', 'size'])
FACE = ['int', 'int', 'int',
		'int', 'int',
		'int', 'int',
		'int', '2int',
		'2int', '3float',
		'mat2x3_float', '3float', '2int']

lightvol = namedlist('lightvol', ['ambient', 'directional', 'dir'])
LIGHTVOL = ['3ubyte', '3ubyte', '2ubyte']

visdata = namedlist('visdata', ['n_vecs', 'sz_vecs', 'vecs'])


class BSP_loader():
	def __init__(self, path):
		self.path = path
		self.magic = ''
		self.version = -1
		self.direntries = []

		self.entities = ''
		self.textures = []
		self.planes = []
		self.nodes = []
		self.leafs = []
		self.leaffaces = []
		self.leafbrushes = []
		self.models = []
		self.brushes = []
		self.brushsides = []
		self.vertices = []
		self.mvertices = []
		self.effects = []
		self.faces = []
		self.lightmaps = []
		self.lightvol = []
		self.visdata = None
		self._file = None
		self._load()

	def _load(self):
		self._file = open(self.path, 'rb')
		self.magic = self._file.read(4).decode('ASCII')
		self.version = self._readInt()
		print(self.magic)
		#Read direntries
		for _ in range(17):
			entry = self.parseEntry(DIRENTRY)
			self.direntries.append(direntry(*entry))


		#Load entities
		self._file.seek(self.direntries[0].offset)
		self.entities = self._file.read(self.direntries[0].length).decode('ASCII')
		self.textures = self.loadEntries(texture, TEXTURE, 1, 72)
		self.planes = self.loadEntries(plane, PLANE, 2, 16)
		self.nodes = self.loadEntries(node, NODE, 3, 36)
		self.leafs = self.loadEntries(leaf, LEAF, 4, 48)


		#Leaffaces
		n_leaffaces = self.direntries[5].length // 4
		self._file.seek(self.direntries[5].offset)
		for _ in range(n_leaffaces):
			self.leaffaces.append(self._readInt())
		#Leafbrushes
		n_leafbrushes = self.direntries[6].length // 4
		self._file.seek(self.direntries[6].offset)
		for _ in range(n_leafbrushes):
			self.leafbrushes.append(self._readInt())

		self.models = self.loadEntries(model, MODEL, 7, 40)
		self.brushes = self.loadEntries(brush, BRUSH, 8, 12)
		self.brushsides = self.loadEntries(brushside, BRUSHSIDE, 9, 8)
		self.vertices = self.loadEntries(vertex, VERTEX, 10, 44)


		#Meshverts
		n_mverts = self.direntries[11].length // 4
		self._file.seek(self.direntries[11].offset)
		for _ in range(n_mverts):
			mvert = self._readInt()
			self.mvertices.append(mvert)


		self.effects = self.loadEntries(effect, EFFECT, 12, 72)
		self.faces = self.loadEntries(face, FACE, 13, 104)


		#Lightmaps
		n_lightmaps = self.direntries[14].length // (128*128*3)
		self._file.seek(self.direntries[14].offset)
		for _ in range(n_lightmaps):
			lm = np.zeros((128, 128, 3), dtype='uint8') # lightmaps are 128 by 128
			for i in range(128):
				for j in range(128):
					lm[i][j][0] = self._readUint()
					lm[i][j][1] = self._readUint()
					lm[i][j][2] = self._readUint()			
			self.lightmaps.append(lm)

		self.lightvol.append(self.loadEntries(lightvol, LIGHTVOL, 15, 8))
		#Visdata
		self._file.seek(self.direntries[16].offset)
		n_vecs = self._readInt()
		sz_vecs = self._readInt()
		vecs = []
		for _ in range(n_vecs * sz_vecs):
			vecs.append(self._file.read(1))
		self.visdata = visdata(n_vecs, sz_vecs, vecs)

		self._file.close()


	def loadEntries(self, entry_type, description, index, size):
		entries = []
		n = self.direntries[index].length // size
		self._file.seek(self.direntries[index].offset)
		for _ in range(n):
			entry = self.parseEntry(description)
			entries.append(entry_type(*entry))
		return entries


	def parseEntry(self, description):
		fields = []
		for f in description:
			if f[0].isdigit():
				tip = f[1:]
				fields.append(tuple([self.parseField(tip) for _ in range(int(f[0]))]))
			elif f[:3] == 'str':
				string = self._file.read(int(f[3:])).decode('ASCII').rstrip('\x00')
				fields.append(string)
			elif f[:3] == 'mat':
				size = tuple([toIntIgnore(s) for s in f.split('x')])
				mat = []
				for _ in range(size[0]):
					mat.append([self.parseField(f.split('_')[1]) for _ in range(size[1])])
				fields.append(mat)
			else:
				fields.append(self.parseField(f))
		return tuple(fields)


	def parseField(self, f):
		if f == 'int':
			return self._readInt()
		elif f == 'float':
			return self._readFloat()
		elif f == 'uint':
			return self._readUint()
		elif f == 'ubyte':
			return int.from_bytes(self._file.read(1), byteorder='little', signed = False)
		else:
			print('Error!!! Can not parse {}'.format(f))


	def _readInt(self):
		return int.from_bytes(self._file.read(INT_SIZE), byteorder='little', signed=True)

	def _readUint(self):
		return int.from_bytes(self._file.read(INT_SIZE), byteorder='little', signed = False)

	def _readFloat(self):
		return struct.unpack('f', self._file.read(FLOAT_SIZE))[0]


	def preload_vertices(self, context):
		vertices = []
		for vertex in self.vertices:
			vertices.extend(list(vertex.position))
			#vertices.extend(vertex.texcoord[0])
			vertices.extend(vertex.texcoord[1])
			#vertices.extend(list(vertex.normal))
			vertices.extend([x / 255.0 for x in vertex.color])
		return context.buffer(struct.pack('%sf' % len(vertices), *vertices))

	def preload_lightmaps(self, context):
		lightmaps = []
		for lightmap in self.lightmaps:
			texture = context.texture((128, 128), 3, lightmap.tobytes())
			lightmaps.append(texture)
		return lightmaps

	'''def preload_textures(self, context):
		for texture in self.textures:
			if texture.tex != 'noshader':
				try:
					img = Image.open(texture.tex + '.jpg')
					tex = context.texture(img.size, 3, img.tobytes())
					texture.tex = tex
				except:
					print(texture.tex)'''

def toIntIgnore(s):
	return int(''.join(c for c in s if c.isdigit()))

