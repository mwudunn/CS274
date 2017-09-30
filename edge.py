from vertex import vertex
import face

class edge:
	def __init__(self): 
		self.is_dual = False
		self.vertex = None
		self.id = None
		self.quad_edge = None
		self.next = None
		self.face = None
		

	def rot(self):
		if self.is_dual:
			return self.quad_edge.edges[(self.id)]
		return self.quad_edge.dual_edges[(1 - self.id)]

	def inv_rot(self):
		if self.is_dual:
			return self.quad_edge.edges[(1 - self.id)]
		return self.quad_edge.dual_edges[self.id]

	def sym(self):
		if self.is_dual:
			return self.quad_edge.dual_edges[(1 - self.id)]
		return self.quad_edge.edges[(1 - self.id)]
	
	def link_quad(self, quad):
		self.quad_edge = quad

	def unlink_quad(self):
		self.quad_edge = None

	def onext(self):
		return self.next

	def oprev(self):
		return self.rot().onext().rot()

	def lnext(self):
		return self.inv_rot().onext().rot()

	def rprev(self):
		return self.sym().onext()

	def get_origin(self):
		return self.vertex

	def set_origin(self, origin): 
		self.vertex = origin
		self.vertex.set_edge(self)

	def get_destination(self):
		return self.sym().vertex

	def set_destination(self, destination):
		self.sym().vertex = destination
		self.sym().vertex.set_edge(self.sym())

	def set_face(self, next_face, is_left):
		if is_left:
			dual_edge = self.inv_rot()
		else:
			dual_edge = self.rot()
		dual_edge.face = next_face
		return next_face.set_edge(self)

	def get_leftface(self):
		return self.inv_rot().face
	
	def get_rightface(self):
		return self.rot().face


class quad_edge:
	def __init__(self):
		self.edges = [edge(), edge()]
		self.dual_edges = [edge(), edge()]
		for i in range(len(self.edges)):
			self.edges[i].id = i
			self.edges[i].link_quad(self)
			self.edges[i].next = self.edges[i]
			self.dual_edges[i].id = i
			self.dual_edges[i].link_quad(self)
			self.dual_edges[i].next = self.dual_edges[(1 - i)]
			self.dual_edges[i].is_dual = True

	def get_edge(self):
		return self.edges[0]

	def get_dual_edge(self):
		return self.dual_edges[0]





