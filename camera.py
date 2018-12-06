import mymath as m
import math
import itertools

WIDTH = 320
HEIGHT = 240

def to_tuple(matrix):
	return tuple(itertools.chain(*matrix))

class Camera():
	# proj --- tuple (fov, near, far)
	def __init__(self, position, direction, proj):
		self.yaw = 0.0
		self.pitch = 0.0
		self.position = position
		self.direction = direction
		self.fov = proj[0]
		self.near = proj[1]
		self.far = proj[2]
		self.proj = None
		self.view = None
		self.w = None
		self.v = None
		self.u = None
		self.delta = 0.0
		self.mouse(0, 0)
		'''up = (0.0, 1.0, 0.0)
		self.w = m.normal( m.sub(self.position, self.direction) )
		self.v = m.normal(m.sub(up, m.scale(self.w, m.dot(up, self.w))))
		self.u = m.cross(self.v, self.w)'''

	def get_view(self):
		if self.view is None:
			self.v = m.cross(self.w, self.u)
			self.view = [[self.u[0], self.v[0], self.w[0], 0.0],
						 [self.u[1], self.v[1], self.w[1], 0.0],
						 [self.u[2], self.v[2], self.w[2], 0.0],
						 [-m.dot(self.u, self.position), -m.dot(self.v, self.position), -m.dot(self.w, self.position), 1.0]]
		return to_tuple(self.view)
	
	def get_proj(self):
		if self.proj is None:
			fov = m.rad(self.fov)
			aspect = 640.0/480.0
			width = 2 * self.near * math.tan(fov/2)
			height = width / aspect
			x = 2 * self.near / width
			y = 2 * self.near / height
			c1 = (2*self.far*self.near)/(self.far - self.near)
			c2 = (self.near + self.far)/(self.far - self.near)

			self.proj = [	[x, 0.0, 0.0, 0.0],
							[0.0, y, 0.0, 0.0],
							[0.0, 0.0, -c2, -1.0],
							[0.0, 0.0, -c1, 0.0]]
		return to_tuple(self.proj)

	def move(self, direction):
		s = self.delta * 100.0
		if direction == 0:
			self.position = m.add(self.position, m.scale(self.w, -s))
		elif direction == 1:
			self.position = m.add(self.position, m.scale(self.w, s))
		elif direction == 2:
			self.position = m.add(self.position, m.scale(self.u, s))
		elif direction == 3:
			self.position = m.add(self.position, m.scale(self.u, -s))
		self.view = None

	def mouse(self, dx, dy):
		coef = self.delta * 20.0
		self.yaw -= m.rad( 90.0 * dx/WIDTH * coef)
		self.pitch += m.rad( 90.0 * dy/HEIGHT * coef )
		self.u = (math.cos(self.yaw), 0.0, -math.sin(self.yaw))
		self.w = (math.sin(self.yaw) * math.cos(self.pitch), -math.sin(self.pitch), math.cos(self.yaw) * math.cos(self.pitch))
		self.view = None

