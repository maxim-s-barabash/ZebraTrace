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


def makePath(fX, fY, T, res=1):
	retx, rety = tuple(_getCoords(fX, fY, T, res))
	if retx:
		return Path([Point(retx[i], rety[i]) for i in range(len(retx))])
	else:
		return None


class Path(object):
	__slots__ = ("node", "fill", "stroke", "strok_width", "close_path")

	def __init__(self, node=None, fill='black', stroke='None',
						strok_width=0, close_path=False):
		self.node = [node, []][node is None]
		self.fill = fill
		self.stroke = stroke
		self.strok_width = strok_width
		self.close_path = close_path

	def __len__(self):
		return len(self.node)

	def __str__(self):
		return "%s" % (self.node)

	def __repr__(self):
		return "Path(%s)" % (self.node)

#	def __iter__(self):
#		#print('Path.__iter__')
#		return iter(self.node)

#	def __getitem__(self, key):
#		return self.node[key]

#	def __setitem__(self, key, value):
#		self.node[key] = value

#	def __add__(self, other):
#		if isinstance(other, Point):
#			self.node.append(other)
#		elif isinstance(other, Path):
#				self.node += other.node
#		return self

#	def __reversed__(self):
#		return reversed(self.node)

#	def append(self, value):
#		self.node.append(value)

#	def reverse(self):
#		self.node.reverse()

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

	def length(self):
		l = 0.0
		p = self.node[0]
		for n in self.node[1:]:
			l += p.distance(n)
			p = n
		return l

	def asSVG(self):
		path = ''
		if len(self.node) > 1:
			path += '<path stroke="%s" stroke-width="%g" fill="%s" ' % (self.stroke, self.strok_width, self.fill)
			path += 'd="M%g,%g' % (self.node[0].x, self.node[0].y)
			path += ''.join(['L%g,%g' % (n.x, n.y) for n in self.node[1:]])
			path += ['"/>\n', 'Z"/>\n'][self.close_path]
		return path

	def strokeToPath(self, style=0):
			"""	Here we take two neighboring points and calculate the angle (alpha), under which there is a line,
			perpendicular to the tangent to the curve. With this angle we hold
			connecting the ends of two parallel curves (right and left) to replace the old (coords),
			separated by a distance that depends on the index of the image.
			"""
			node = self.node
			right = []
			left = []
			p0, p1, pn, ps = node[0], node[1], node[-1], node[-2]
			# if directions are not equal
			if (p1.x - p0.x) * (p1.x - pn.x) < 0 or \
				(p1.y - p0.y) * (p1.y - pn.y) < 0:
				# extrapolation
				pre_x, pre_y = 2 * p0.x - p1.x, 2 * p0.y - p1.y
				node.append(Point(2 * pn.x - ps.x, 2 * pn.y - ps.y))
			else:
				pre_x, pre_y = ps.x, ps.y
				node.append(p1)

			for i in range(len(node) - 1):
				x, y = node[i].x, node[i].y
				x1, y1 = node[i + 1].x, node[i + 1].y
				if pre_x < x1:
					alpha = atan((y1 - pre_y) / (x1 - pre_x)) + pi / 2
				elif pre_x == x1:
					alpha = [pi, 0][y1 < pre_y]
				else:
					alpha = atan((y1 - pre_y) / (x1 - pre_x)) + pi / 2 + pi

				d = node[i].d
				dx = d * cos(alpha)
				dy = d * sin(alpha)

				if style == 0:
					right.append(Point(x + dx, y + dy))
					left.append(Point(x - dx, y - dy))
				elif style == 1:
					right.append(Point(x + dx, y + dy))
					left.append(Point(x, y))
				elif style == 2:
					right.append(Point(x, y))
					left.append(Point(x - dx, y - dy))
				elif style == 3:
					dx2 = d * 2 * cos(alpha)
					dy2 = d * 2 * sin(alpha)
					right.append(Point(x + dx2, y + dy2))
					left.append(Point(x + dx, y + dy))
				elif style == 4:
					dx2 = d * 2 * cos(alpha)
					dy2 = d * 2 * sin(alpha)
					right.append(Point(x - dx, y - dy))
					left.append(Point(x - dx2, y - dy2))
				pre_x, pre_y = x, y

			left.reverse()
			self.node = right + left
			self.fill = self.stroke
			self.stroke = 0
			self.close_path = True


def _getCoords(fX, fY, T, res=1):
	dT = float(T[1] - T[0])
	step = int(dT * res)
	if step > 1:
		seg = dT / step
		tl = [T[0] + seg * i for i in range(step + 1)]
		return (list(map(fX, tl)), list(map(fY, tl)))
	else:
		return (None, None)
