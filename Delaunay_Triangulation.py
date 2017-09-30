import vertex
import face
import edge
import geompreds
import numpy as np
import time
import sys

#Generate the .ele file
def create_ele(output_file, face_set):
	f = open(output_file, "w+")
	f.write(str(len(face_set) - 1) + " 3 0")
	counter = 0
	for each in face_set:
		edge = each.get_edge()
		array = []
		while edge.lnext() != each.get_edge():
			vertex_id = int(edge.get_origin().id)
			array.append(vertex_id)
			edge = edge.lnext()
		vertex_id = int(edge.get_origin().id)
		array.append(vertex_id)
		if len(array) <= 3:
			f.write("\n")
			counter += 1
			f.write(str(counter))
			for position in array:
				f.write(" " + str(position))


def splice(a, b): 
	alpha = a.onext().rot()
	beta = b.onext().rot()
	a_next = b.onext()
	b_next = a.onext()
	alp_next = beta.onext()
	bet_next = alpha.onext()
	a.next = a_next
	b.next = b_next
	alpha.next = alp_next
	beta.next = bet_next

#Connect two quad-edges
def connect(edge1, edge2): #regular edges
	create_edge = edge.quad_edge()
	create_face = face.face()
	create_edge.get_edge().set_origin(edge1.get_destination())
	create_edge.get_edge().set_destination(edge2.get_origin())
	create_edge.get_edge().set_face(edge2.get_leftface(), True)
	splice(create_edge.get_edge(), edge1.lnext())
	splice(create_edge.get_edge().sym(), edge2)
	set_faces(create_edge.get_edge().sym(), create_face)
	return create_edge.get_edge()

def delete_edge(edge):
	edge1 = edge.oprev()
	edge2 = edge.sym().oprev()
	if edge1 == edge.sym():
		edge1 = edge2
	splice(edge2, edge.sym())
	splice(edge1, edge)
	edge1.get_origin().set_edge(edge1)
	edge1.get_leftface().set_edge(edge1)
	edge2.get_leftface().set_edge(edge2)
	set_faces(edge1, edge2.get_leftface())
	edge.unlink_quad()

#Set the face pointer of all the edges that surround a face
def set_faces(edge, left_face):
	edge.set_face(left_face, True)
	next_edge = edge.lnext()
	while next_edge != edge:
		next_edge.set_face(left_face, True)
		next_edge = next_edge.lnext()

#Check if a vertex lies to the right of an edge
def rightof(p, e):
	return geompreds.orient2d(p.position, e.get_destination().position, e.get_origin().position) > 0

#Check if a vertex lies to the left of an edge
def leftof(p, e):
	return geompreds.orient2d(p.position, e.get_origin().position, e.get_destination().position) > 0

#Check if a vertex lies in a valid triangle (i.e. the triangle is Delaunay)
def valid(e, basel):
	return rightof(e.get_destination(), basel)


def read_in(string):
	file = open(string).read()
	points = []
	for pt in file.splitlines():
		converted = pt.split()
		converted[0] = int(converted[0])
		converted[1] = float(converted[1])
		converted[2] = float(converted[2])
		points.append(tuple(converted))
	points = points[1:]
	points = list(set(points))
	for i in range(len(points)):
		points[i] = list(points[i])
	def get(o):
		return (o[1], o[2])
	points.sort(key=get)
	return points

def filter(arr, median, x_coord=True):
	l, r = [], []
	index = 1
	if not x_coord:
		index = 2
	for i in range(len(arr)):
		if arr[i][index] <= median:
			l.append(arr[i])
		else:
			r.append(arr[i])
	l, r = np.array(l), np.array(r)
	return l, r

#Get the edges along the convex hull
def get_hull_edges(edge1, edge2):
	edge_result = []
	for i in range(2):
		first_iteration = True
		start_edge = edge1
		if i == 1:
			start_edge = edge2
		next_edge = start_edge
		while first_iteration or next_edge != start_edge:
			first_iteration = False
			if i == 1:
				orient_next = leftof(next_edge.onext().get_destination(), next_edge)
				orient_prev = leftof(next_edge.oprev().get_destination(), next_edge)
			else:
				orient_next = rightof(next_edge.onext().get_destination(), next_edge)
				orient_prev = rightof(next_edge.oprev().get_destination(), next_edge)
			if not orient_next and not orient_prev:
				break
			next_edge = next_edge.onext()
		edge_result.append(next_edge)
	return edge_result


def set_variables(arr, var, xmin, xmax, gt):
	for i in range(len(arr)):
		if gt:
			if arr[i].position[1] > var.position[1]:
				var = arr[i]
		else:
			if arr[i].position[1] < var.position[1]:
				var = arr[i]
		if arr[i].position[0] < xmin.position[0]:
			xmin = arr[i]
		elif arr[i].position[0] > xmax.position[0]:
			xmax = arr[i]
	return [var, xmax, xmin]


#Perform the Delaunay Triangulation by alternating between vertical and horizontal cuts
def DT_alternating_cuts(points, alternate=False, vertical_cuts=True):

	if len(points) == 2:
		edge1 = edge.quad_edge().get_edge()
		origin, destination = vertex.vertex(), vertex.vertex()
		origin.set(points[0][1], points[0][2], points[0][0])
		destination.set(points[1][1], points[1][2], points[1][0])
		edge1.set_origin(origin)
		edge1.set_destination(destination)
		edge1.set_face(face.face(), True)
		edge1.set_face(edge1.get_leftface(), False)

		return [edge1, edge1.sym(), [origin, destination]]

	elif len(points) == 3:
		v1, v2, v3 = vertex.vertex(), vertex.vertex(), vertex.vertex()
		v1.set(points[0][1], points[0][2], points[0][0])
		v2.set(points[1][1], points[1][2], points[1][0])
		v3.set(points[2][1], points[2][2], points[2][0])

		edge1, edge2 = edge.quad_edge().get_edge(), edge.quad_edge().get_edge()
		splice(edge1.sym(), edge2)
		edge1.set_destination(v2)
		edge2.set_destination(v3)
		edge1.set_origin(v1)
		edge2.set_origin(v2)
		edge1.set_face(face.face(), True)
		edge2.set_face(edge1.get_leftface(), True)
		edge1.set_face(edge1.get_leftface(), False)
		edge2.set_face(edge1.get_leftface(), False)
	
		if geompreds.orient2d(v1.position, v2.position, v3.position) > 0:
			c = connect(edge2, edge1)
			return [edge1, edge2.sym(), [v1, v2, v3]]
		elif geompreds.orient2d(v1.position, v3.position, v2.position) > 0:
			c = connect(edge2, edge1)
			return [c.sym(), c, [v1, v2, v3]]
		else:
			return [edge1, edge2.sym(), [v1, v2, v3]]
	else:
		if vertical_cuts:
			med = np.median(points[:,1])
			L, R = filter(points, med, True)
			if alternate:
				ldo, ldi, lvertices = DT_alternating_cuts(L, alternate=alternate, vertical_cuts=False)
				rdi, rdo, rvertices = DT_alternating_cuts(R, alternate=alternate, vertical_cuts=False)
			else:
				ldo, ldi, lvertices = DT_alternating_cuts(L)
				rdi, rdo, rvertices = DT_alternating_cuts(R)
		else:
			med = np.median(points[:,2])
			L, R = filter(points, med, False)

			ldo, ldi, lvertices = DT_alternating_cuts(L, alternate=alternate)
			rdi, rdo, rvertices = DT_alternating_cuts(R, alternate=alternate)
		if not vertical_cuts:
			bot_max, overall_xmax, overall_xmin = set_variables(lvertices, lvertices[0], lvertices[0], lvertices[0], True)
			top_min, overall_xmax, overall_xmin = set_variables(rvertices, rvertices[0], overall_xmin, overall_xmax, False)

			rdi, ldi = get_hull_edges(top_min.edge, bot_max.edge)

		while True:
			if leftof(rdi.get_origin(), ldi):
				ldi = ldi.lnext()
			elif rightof(ldi.get_origin(), rdi):
				rdi = rdi.rprev()
			else:
				break
		basel = connect(rdi.sym(), ldi)
		if ldi.get_origin() == ldo.get_origin():
			ldo = basel.sym()
		if rdi.get_origin() == rdo.get_origin():
			rdo = basel
		while True:
			lcand = basel.sym().onext()
			if valid(lcand, basel):
				while geompreds.incircle(basel.get_destination().position, basel.get_origin().position,
					lcand.get_destination().position, lcand.onext().get_destination().position) > 0:
					t = lcand.onext()
					delete_edge(lcand)
					lcand = t
			rcand = basel.oprev()
			if valid(rcand, basel):
				while geompreds.incircle(basel.get_destination().position, basel.get_origin().position,
					rcand.get_destination().position, rcand.oprev().get_destination().position) > 0:
					t = rcand.oprev()
					delete_edge(rcand)
					rcand = t
			if not valid(lcand, basel) and not valid(rcand, basel):
				break
			rc_b = valid(rcand, basel) and geompreds.incircle(lcand.get_destination().position, lcand.get_origin().position,
				rcand.get_origin().position, rcand.get_destination().position) > 0
			if not valid(lcand, basel) or rc_b:
				basel = connect(rcand, basel.sym())
			else:
				basel = connect(basel.sym(), lcand.sym())
		if not vertical_cuts:
			ldo, rdo = get_hull_edges(overall_xmin.get_edge(), overall_xmax.get_edge())

	return [ldo, rdo, lvertices + rvertices]

#Retrieve the set of faces for a Delaunay Triangulation
def retrieve_triangulation(vertices):
	face_set = set()
	for vertex in vertices:
		first_iteration = True
		next_edge = vertex.edge
		while first_iteration or next_edge != vertex.edge:
			first_iteration = False
			if next_edge.get_leftface() not in face_set:
				face_set.add(next_edge.get_leftface())
			if next_edge.get_rightface() not in face_set:
				face_set.add(next_edge.get_rightface())
			next_edge = next_edge.onext()
	return face_set

def main():
	input_file = sys.argv[1]
	output_file = sys.argv[2]
	alternate = sys.argv[3]
	points = read_in(input_file) 
	points = np.array(points)
	start = time.time()
	if alternate.lower() == "false":
		alternate = False
	left_output, right_output, vertices = DT_alternating_cuts(points, alternate=alternate)
	end = time.time()
	print end - start
	face_set = retrieve_triangulation(vertices)
	create_ele(output_file, face_set)

main()
