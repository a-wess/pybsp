import math

def dot(v1, v2):
	assert len(v1) == len(v2)
	r = 0
	for i in range(len(v1)):
		r += v1[i] * v2[i]
	return r

def add(v1, v2):
	assert len(v1) == len(v2)
	return tuple([v1[i] + v2[i] for i in range(len(v1))])


def sub(v1, v2):
	assert len(v1) == len(v2)
	return tuple([v1[i] - v2[i] for i in range(len(v1))])

def neg(v1):
	return tuple([-x for x in v1])

def cross(v1, v2):
	assert len(v1) == 3
	return (v1[1]*v2[2] - v2[1]*v1[2], v2[0]*v1[2] - v1[0]*v2[2], v1[0]*v2[1] - v2[0]*v1[1])

def scale(v, c):
	return tuple([c*vi for vi in v])

def rad(deg):
	return deg * (math.pi / 180)

def normal(v):
	if v[0] == 0 and v[1] == 0 and v[2] == 0:
		return v
	n = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
	return (v[0]/n, v[1]/n, v[2]/n)

def mat4_mult(m1, m2):
	m = [[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0],[0.0, 0.0, 0.0, 0.0]]
	for i in range(4):
		for j in range(4):
			m[i][j] = m1[i][0]*m2[0][j]+m1[i][1]*m2[1][j]+m1[i][2]*m2[2][j]+m1[i][3]*m2[3][j]
	return m

#p_list is a list of control points
def B_quad(p_list, t):
	assert len(p_list) == 3
	vertex = [0.0, 0.0, 0.0]
	coefs = [(1-t)**2, (1-t), t**2]
	for i in range(3):
		vertex[0] += coefs[i] * p_list[i][0]
		vertex[1] += coefs[i] * p_list[i][1]
		vertex[2] += coefs[i] * p_list[i][2]
	return tuple(vertex)

