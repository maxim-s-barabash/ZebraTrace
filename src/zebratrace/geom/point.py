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

from math import hypot

EPSILON = 0.000000001


class Point(object):
	__slots__ = ("x", "y", "d")

	def __init__(self, x=0, y=0, d=0):
		self.x = float(x)
		self.y = float(y)
		self.d = float(d)

	def __len__(self):
		return 1

	def __eq__(self, other):
		deltaY = abs(other.y - self.y)
		deltaX = abs(other.x - self.x)
		return deltaY < EPSILON and deltaX < EPSILON

	def __ne__(self, other):
		return not(self.__eq__(other))

	def __str__(self):
		return "[%g,%g]" % (self.x, self.y)

	def __repr__(self):
		return "Point(%g,%g)" % (self.x, self.y)

#	def __iter__(self):
#		return iter((self.x,self.y))

#	def __getitem__(self, key):
#		return (self.x, self.y)[key]

	def distance(self, other):
		return hypot((self.x - other.x), (self.y - other.y))


def distance(a, b):
	return hypot((b.x - a.x), (b.y - a.y))
