#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	Copyright 2012 Maxim.S.Barabash <maxim.s.barabash@gmail.com>
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

from math import hypot, atan, pi, cos, sin, atan2
from .point import Point
from .style import Style



def makePathData(fX, fY, T, res=1, close_path=False):
	dT = float(T[1] - T[0])
	step = int(dT * res)
	if step > 1:
		seg = dT / step
		tl = [T[0] + seg * i for i in range(step + 1)]
		retx, rety = list(map(fX, tl)), list(map(fY, tl))
		p = PathData([Point(retx[i], rety[i]) for i in range(len(retx))], close_path)
		return p
	else:
		return None


def split(splitPath, threshold=0.0):
	paths = []
	path = []
	end = False
	leng = len(splitPath.node)
	for i in range(leng):
		n = splitPath.node[i]
		d = n.d
		if d <= threshold and len(path) > 0:
			path.append(n)
			end = True
		elif d > threshold:
			path.append(n)

		if end or i == leng - 1:
			paths.append(PathData(path))
			path = []
			end = False

		if i < leng - 1 and d <= threshold and \
						splitPath.node[i + 1].d > threshold:
			path.append(n)

	return Path(paths)


class PathData(object):
	__slots__ = ("node", "close_path")

	def __init__(self, node=None, close_path=False):
		self.node = [node, []][node is None]
		self.close_path = close_path

	def __len__(self):
		return len(self.node)

	def __str__(self):
		return "%s" % (self.node)

	def __repr__(self):
		return "PathData(%s)" % (self.node)

	def boundingRect(self):
		node = self.node
		lax = lambda a: a.x
		lay = lambda a: a.y
		maxX, minX = max(node, key=lax), min(node, key=lax)
		maxY, minY = max(node, key=lay), min(node, key=lay)
		return (minX.x, minY.y, maxX.x - minX.x, maxY.y - minY.y)

	def height(self):
		node = self.node
		lax = lambda a: a.x
		maxX, minX = max(node, key=lax), min(node, key=lax)
		return (maxX.x - minX.x)

	def width(self):
		node = self.node
		lay = lambda a: a.y
		maxY, minY = max(node, key=lay), min(node, key=lay)
		return (maxY.y - minY.y)

	def countNodes(self):
		return len(self.node)

	def length(self):
		l = 0.0
		p = self.node[0]
		for n in self.node[1:]:
			l += p.distance(n)
			p = n
		return l

	def strokeToPath(self, writing=0):
			if len(self.node) < 2:
				return

			node = self.node
			right = []
			left = []

			p0, p1, pn, ps = node[0], node[1], node[-1], node[-2]
			# if directions are not equal
			if (p1.x - p0.x) * (p1.x - pn.x) < 0. or \
				(p1.y - p0.y) * (p1.y - pn.y) < 0.:
				# extrapolation
				pre_x, pre_y = 2 * p0.x - p1.x, 2. * p0.y - p1.y
				node.append(Point(2 * pn.x - ps.x, 2. * pn.y - ps.y))
			else:
				pre_x, pre_y = ps.x, ps.y
				node.append(p1)

			for i in range(len(node) - 1):
				x, y = node[i].x, node[i].y
				x1, y1 = node[i + 1].x, node[i + 1].y
				if pre_x < x1:
					alpha = atan((y1 - pre_y) / (x1 - pre_x)) + pi / 2.
				elif pre_x == x1:
					alpha = [pi, 0.][y1 < pre_y]
				else:
					alpha = atan((y1 - pre_y) / (x1 - pre_x)) + pi / 2. + pi

				d = node[i].d
				dx = d * cos(alpha)
				dy = d * sin(alpha)

				dx2 = d * 2 * cos(alpha)
				dy2 = d * 2 * sin(alpha)

				if writing == 0:
					right.append(Point(x + dx, y + dy))
					left.append(Point(x - dx, y - dy))
				elif writing == 1:
					right.append(Point(x + dx2, y + dy2))
					left.append(Point(x, y))
				elif writing == 2:
					right.append(Point(x, y))
					left.append(Point(x - dx2, y - dy2))
				elif writing == 3:
					right.append(Point(x + dx2, y + dy2))
					left.append(Point(x + dx, y + dy))
				elif writing == 4:
					right.append(Point(x - dx, y - dy))
					left.append(Point(x - dx2, y - dy2))
				pre_x, pre_y = x, y

			left.reverse()
			self.node = right + left
			self.close_path = True




class Path(object):
	__slots__ = ("path", "style", "writing")

	def __init__(self, path=None, style=None, writing=0):
		self.path = [path, []][path is None]
		self.style = [style, Style()][style is None]
		self.writing = writing

	def __len__(self):
		return len(self.path)

	def __str__(self):
		return "%s" % (self.path)

	def __repr__(self):
		return "Path(%s)" % (self.path)

	def __iter__(self):
		return iter(self.path)

	def __getitem__(self, key):
		return self.path[key]

	def __setitem__(self, key, value):
		self.path[key] = value

	def __add__(self, other):
		if isinstance(other, PathData):
			self.path.append(other)
		elif isinstance(other, Paths):
				self.path += other.path
		return self

	def __reversed__(self):
		return reversed(self.path)

	def append(self, value):
		self.path.append(value)

	def reverse(self):
		self.path.reverse()

	def boundingRect(self):
		pass

	def height(self):
		pass

	def width(self):
		pass

	def length(self):
		l = 0
		for p in self.path[:]:
			l += p.length()
		return l

	def strokeToPath(self, writing=None):
		
		if writing is None:
			writing = self.writing

		for p in self.path[:]:
			p.strokeToPath(writing)

	def countNodes(self):
		c = 0
		for p in self.path[:]:
			c += p.countNodes()
		return c

	def asSVG(self):
		path = ''
		path += '<path stroke="%s" stroke-width="%g" fill="%s" d="' % (self.stroke, self.strok_width, self.fill)
		for p in self.path:
			if len(p) < 2:
				continue
			path += 'M%g,%g' % (p.node[0].x, p.node[0].y)
			path += ''.join(['L%g,%g' % (n.x, n.y) for n in p.node[1:]])
			path += [' ', 'Z'][p.close_path]
		path += '"/>\n'
		return path
