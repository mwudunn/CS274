class vertex:
	def __init__(self): #position is a <x,y>
		self.position = None
		self.edge = None
		self.id = None
		self.face = None

	def set_edge(self, e):
		if e is not None:
			self.edge = e

	def set(self, x, y, id_):
		self.position = (x, y)
		self.id = id_

	def get_edge(self):
		return self.edge

	def remove_edge(self, e):
		next_edge = e.origin_next()
		if next_edge is not None:
			self.edge = next_edge
		else:
			self.edge = None