# -*- coding: utf-8 -*-
# pure-Python Douglas-Peucker line simplification/generalization
#
# this code was written by Schuyler Erle <schuyler@nocat.net> and is
#   made available in the public domain.
#
# the code was ported from a freely-licensed example at
#   http://www.3dsoftware.com/Cartography/Programming/PolyLineReduction/
#
# the original page is no longer available, but is mirrored at
#   http://www.mappinghacks.com/code/PolyLineReduction/

"""

>>> line = [(0,0),(1,0),(2,0),(2,1),(2,2),(1,2),(0,2),(0,1),(0,0)]
>>> simplify_points(line, 1.0)
[(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]

>>> line = [(0,0),(0.5,0.5),(1,0),(1.25,-0.25),(1.5,.5)]
>>> simplify_points(line, 0.25)
[(0, 0), (0.5, 0.5), (1.25, -0.25), (1.5, 0.5)]

"""

import math


def simplify_points(pts, tolerance):
	anchor = 0
	floater = len(pts) - 1
	stack = []
	keep = set()

	stack.append((anchor, floater))
	while stack:
		anchor, floater = stack.pop()

		# initialize line segment
		if pts[floater] != pts[anchor]:
			anchorX = float(pts[floater][0] - pts[anchor][0])
			anchorY = float(pts[floater][1] - pts[anchor][1])
			seg_len = math.sqrt(anchorX ** 2 + anchorY ** 2)
			# get the unit vector
			anchorX /= seg_len
			anchorY /= seg_len
		else:
			anchorX = anchorY = seg_len = 0.0

		# inner loop:
		max_dist = 0.0
		farthest = anchor + 1
		for i in range(anchor + 1, floater):
			dist_to_seg = 0.0
			# compare to anchor
			vecX = float(pts[i][0] - pts[anchor][0])
			vecY = float(pts[i][1] - pts[anchor][1])
			seg_len = math.sqrt(vecX ** 2 + vecY ** 2)
			# dot product:
			proj = vecX * anchorX + vecY * anchorY
			if proj < 0.0:
				dist_to_seg = seg_len
			else:
				# compare to floater
				vecX = float(pts[i][0] - pts[floater][0])
				vecY = float(pts[i][1] - pts[floater][1])
				seg_len = math.sqrt(vecX ** 2 + vecY ** 2)
				# dot product:
				proj = vecX * (-anchorX) + vecY * (-anchorY)
				if proj < 0.0:
					dist_to_seg = seg_len
				else:  # calculate perpendicular distance to line (pythagorean theorem):
					dist_to_seg = math.sqrt(abs(seg_len ** 2 - proj ** 2))
				if max_dist < dist_to_seg:
					max_dist = dist_to_seg
					farthest = i

		if max_dist <= tolerance:  # use line segment
			keep.add(anchor)
			keep.add(floater)
		else:
			stack.append((anchor, farthest))
			stack.append((farthest, floater))

	keep = list(keep)
	keep.sort()
	return [pts[i] for i in keep]

if __name__ == "__main__":
	import doctest
	doctest.testmod()
