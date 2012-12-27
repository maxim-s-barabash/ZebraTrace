#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================
#
# FunctionPlotter
#
# Module for drawing graphs of functions
# Python 2.6, Qt4 4.6
#
# Содержимое этого файла — общественное достояние.
#
# The contents of this file are dedicated to the public domain.
#
# =============================================================


import sys
import os
from math import *
#to trace the image is used PyQt4
#(http://www.riverbankcomputing.co.uk/software/pyqt/download)

from PyQt4.QtGui import QImage, QColor
from ..utils import xrange
sys.setcheckinterval(0xfff)


GRAYSCALE_COLORTABLE = [QColor(i, i, i).rgb() for i in xrange(256)]
DESATURATE_COLORTABLE = [QColor(6*i//10, i, i//5).rgb() for i in xrange(256)]


class FuncPlotter:
	def __init__(self, wh, rect, grid_lines=0, trace_image='', width_range=[0.1, 2]):
		"""Draws the graphics functions.

		Parameters:
		wh			- list [width, height] specifying the size of the image in pixels SVG
		rect		- list [x1, y1, x2, y2] - border coordinate plane
		grid_lines	- an integer specifying the number of grid lines, 0 - no grid
		trace_image	- a string specifying the name of the image file to trace
		width_range	- a list of two values ​​defining the range of thickness in the trace line
		"""
		self.x1, self.y1 = float(rect[0]), float(rect[1])
		self.x2, self.y2 = float(rect[2]), float(rect[3])

		self.dx = float(self.x2 - self.x1)
		self.dy = float(self.y2 - self.y1)

		self.w, self.h = float(wh[0]), float(wh[1])

		# Resolution field in units per pixel SVG
		self.scale = self.dx / self.w

		self.grid = grid_lines
		self.trace_image = trace_image
		self.width_range = width_range

		self.data = []
		self.img = None

		if trace_image and os.path.exists(trace_image):
			# image tracing shall consist of 256 index colors
			# ranked by the number of white (grayscale)
			img = QImage(trace_image)
			img.colorCount()

			colortable = [DESATURATE_COLORTABLE,
							GRAYSCALE_COLORTABLE][img.isGrayscale()]

			self.img = img.convertToFormat(QImage.Format_Indexed8, colortable)
			self.img_w, self.img_h = self.img.width(), self.img.height()
			self.img_colors = float(self.img.colorCount() - 1)

	def _generate_path(self, coords=[], color='black', width=1, close_path=False):
		"""Generates <path/> element with the specified parameters and coordinates.

		The coordinates are passed as [[x1, y1], [x2, y2], [x3, y3], ...].
		"""
		if not coords:
			coords = self.coords

		path = '\n\t\t<path stroke="%s" stroke-width="%s" d="M%f,%f ' % (color, width * self.scale, coords[0][0], coords[0][1])
		path += ''.join(['L%f,%f ' % (x, y) for x, y in coords[1:]]) + ['"/>', 'Z"/>'][close_path]

		self.data.append(path)

	def _trace_image(self):
		"""Changes the coordinates (coords) curve as a function of the image.

		Here we take two neighboring points and calculate the angle (alpha), under which there is a line,
		perpendicular to the tangent to the curve. With this angle we hold
		connecting the ends of two parallel curves (right and left) to replace the old (coords),
		separated by a distance that depends on the index of the image.
		"""
		coords = self.coords

		delta = (self.width_range[1] - self.width_range[0]) / 2.0
		min_width = self.width_range[0] / 2.0

		right = coords[:]
		left = coords[:]
		# OPTIMIZATION
		canvas_x1 = self.x1
		canvas_y1 = self.y1
		canvas_dx = self.dx
		canvas_dy = self.dy
		img_w = self.img_w
		img_h = self.img_h
		img_colors = self.img_colors
		img_pixelIndex = self.img.pixelIndex
		scale = self.scale

		pre_x, pre_y = coords[-1]
		for i, [x, y] in enumerate(coords):
			if pre_x < x:
				alpha = atan((y - pre_y) / (x - pre_x)) + pi/2
			elif pre_x == x:
				alpha = pi / 2
			else:
				alpha = atan((y - pre_y) / (x - pre_x)) + pi/2 + pi

			pixel_x = int((x - canvas_x1) / canvas_dx * img_w)
			pixel_y = int((y - canvas_y1) / canvas_dy * img_h)

			if pixel_x >= 0 and pixel_x < img_w and pixel_y >= 0 and pixel_y < img_h:
				k = 1 - img_pixelIndex(pixel_x, pixel_y) / img_colors
			else:
				k = 0

			d = (min_width + k * delta) * scale

			dx = d * cos(alpha)
			dy = d * sin(alpha)

			right[i] = [x + dx, y + dy]
			left[i] = [x - dx, y - dy]

			pre_x, pre_y = x, y

		left.reverse()
		self.coords = right + left + [right[0]]

	def _getCoords(self, fX, fY, T, res=1, polar_coord=False):
		if polar_coord and fY:
			fR, fT = fX, fY
			fX = lambda a: fR(a) * cos(fT(a))
			fY = lambda a: fR(a) * sin(fT(a))
		elif not fY:                            # If only the function x
			fR = fX                             # then consider the polar coordinates
			fX = lambda a: fR(a) * cos(a)
			fY = lambda a: fR(a) * sin(a)
		dT = float(T[1] - T[0])
		resolution = int(dT * res)
		tl = [T[0] + dT / resolution * i for i in xrange(resolution + 1)]
		return list(map(fX, tl)), list(map(fY, tl))

	def auto_resolution(self, fX, fY, T, polar_coord=False):
		coordX, coordY = self._getCoords(fX, fY, T, res=0.25 / self.scale, polar_coord=polar_coord)
		rX = max(coordX) - min(coordX)
		rY = max(coordY) - min(coordY)
		return int(max(rX, rY) * 0.5)

	def append_func(self, fX, fY, T, res=1, color='black', width=3, close_path=True, tolerance=0.0, polar_coord=False):
		"""Adds a graph of the functions fX (t) and fY (t).

		fX			- a function of one variable, calculates the coordinates of x or
						function of the radius of the corner, if the following option (fY) returns False
		fY			- function of one variable that calculates the y-coordinate, or None
		T			- a list of two values ​​defining the range of the variable
		color		- a string that specifies the stroke color of the curve, you can use named values
						of the SVG specification, or 'none'
		width		- the thickness of the circuit
		close_path	- parameter that indicates whether or not to close the curve
		tolerance	- it simplifies a line by reducing the number of points by some tolerance.
		"""
		coordX, coordY = self._getCoords(fX, fY, T, res / self.scale, polar_coord)
		self.coords = list(zip(coordX, coordY))

		if self.img:                            # if there is a picture, tracing
			self._trace_image()                 # (the result is written to self.coords)

		# Douglas-Peucker line simplification.
		if tolerance > 0.0:
			from .dp import simplify_points
			self.coords = simplify_points(self.coords, tolerance * self.scale)

		self._generate_path([], color, width, close_path)

	def plot(self, file_name='plot.svg'):
		""" Saves the file generated <path/> SVG.
		"""
		if self.grid:                           # if you need a grid, then draw it with a thickness of default and a dark line in the center
			g = self.grid
			for i in xrange(g + 1):
				self._generate_path([[self.x1 + self.dx / g * i, self.y1], \
									[self.x1 + self.dx / g * i, self.y2]], ['grey', 'lightgrey'][bool(i - g / 2)])
				self._generate_path([[self.x1, self.y1 + self.dy / g * i], \
									[self.x2, self.y1 + self.dy / g * i]], ['grey', 'lightgrey'][bool(i - g / 2)])

		header = """<?xml version="1.0" encoding="utf-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="none" """
		header += """width="%i" height="%i" viewBox="%f %f %f %f">\n\t<g fill="%s" fill-rule="evenodd">\n""" % \
					(self.w, self.h, self.x1, self.y1, self.dx, self.dy, ['none', 'black'][bool(self.img)])
		# imag = '  <image y="-1" x="-1" xlink:href="%s" height="2" width="2" opacity=".2" />' % (self.trace_image)
		footer = "\n\n\t</g>\n\n</svg>"

		f = open(file_name, 'w')                # write to file
		f.write(header)
		# f.write(imag)
		f.write(''.join(reversed(self.data)))
		f.write(footer)
		f.close()


# Example of use:
if __name__ == '__main__':

	image_size = [500, 500]
	dimensions = [-1, -1, 1, 1]

	fp = FuncPlotter(image_size, dimensions, grid_lines=20)

	curve_resolution = 0.05
	width = 2

	# graph in rectangular coordinates
	x = lambda t: t
	y = lambda t: 0.5 * sin(t * pi)
	fp.append_func(x, y, [-1, 1], curve_resolution, 'green', width)

	# graph in polar coordinates in the uniformly accelerated carbon
	r = lambda a: sin(a * 2)
	fp.append_func(r, None, [0, 2 * pi], curve_resolution, 'red', width)

	fp.plot()
