The aim of this project was to implement Delaunay Triangulation using the Quad-Edge data structure, as described here:
https://dl.acm.org/citation.cfm?doid=282918.282923

The command-line statement to execute the code is:
python Delaunay_Triangulation.py input-file output-file alternate

Where input-file is the .node file, output-file creates an output file of the same name, and alternate is "false" if the recursive vertical algorithm is requested, and anything else otherwise.

The alternating cuts algorithm is fastest for point sets distributed similar to a square, because after cutting a square (for example) in half, the left and right point sets will look like rectangles. If it is cut vertically in half again, the resulting rectangles get even skinnier. During each merge step, the hulls of the two sets will be all along the long vertical side, so many hull edges will have to be merged (Much like in the figure figure for 3.), except rotated).
With alternating cuts, the square does not get transformed into many skinny rectangles, but instead many smaller squares. This means that the merge step will iterate over far fewer hull edges, improving runtime.
