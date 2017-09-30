class face:
	def __init__(self): 
		self.position = None
		self.edge = None

	def set_edge(self, e):
		if e is not None:
			self.edge = e

	def get_edge(self):
		return self.edge
		
	def remove_edge(self, e):
		if self.edge == e:
			next_edge = e.origin_next()
			if next_edge is not None:
				self.edge = next_edge
			else:
				self.edge = None