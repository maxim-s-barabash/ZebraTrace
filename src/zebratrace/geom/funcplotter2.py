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
from .path import makePathData, split
#from .point import Point


SIMPLIFICATION = 1

if SIMPLIFICATION == 0:
	# Douglas-Peucker line simplification.
	from .dp import simplify_points
else:
	# Visvalingam line simplification.
	from .visvalingam import simplify_visvalingam_whyatt as simplify_points


class FuncPlotter:
	def __init__(self, wh, bound, grid_lines=0, trace_image='', width_range=[0.1, 2]):
		"""Draws the graphics functions.

		Parameters:
		wh			- list [width, height] specifying the size of the image in pixels SVG
		bound		- list [x1, y1, x2, y2] - border coordinate plane
		grid_lines	- an integer specifying the number of grid lines, 0 - no grid
		trace_image	- a string specifying the name of the image file to trace
						or QImage object
		width_range	- a list of two values defining the range of thickness in the trace line
		"""
		self.x1, self.y1 = float(bound[0]), float(bound[1])
		self.x2, self.y2 = float(bound[2]), float(bound[3])

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

		if isinstance(trace_image, QImage):
			self.img = trace_image
		elif trace_image and os.path.exists(trace_image):
			# image tracing shall consist of 256 index colors
			# ranked by the number of white (grayscale)
			from .image import grayscale
			self.img = QImage(trace_image)
			self.img = grayscale(self.img)

		if trace_image:
			self.img_w, self.img_h = self.img.width(), self.img.height()
			self.img_colors = float(self.img.colorCount() - 1)
			self.img_pixelIndex = self.img.pixelIndex

	def _trace_image(self, path, width_range):
		"""Changes the coordinates (coords) curve as a function of the image.

		Here we take two neighboring points and calculate the angle (alpha), under which there is a line,
		perpendicular to the tangent to the curve. With this angle we hold
		connecting the ends of two parallel curves (right and left) to replace the old (coords),
		separated by a distance that depends on the index of the image.
		"""

		delta = (width_range[1] - width_range[0]) / 2.0
		min_width = width_range[0] / 2.0

		# OPTIMIZATION
		img_pixelIndex = self.img_pixelIndex
		img_w, img_h = self.img_w, self.img_h
		img_colors = self.img_colors
		scale = self.scale

		canvas_x1 = self.x1
		canvas_y1 = self.y1
		canvas_dx = self.dx / img_w
		canvas_dy = self.dy / img_h

		for i in range(len(path.node)):
			x, y = path.node[i].x, path.node[i].y
			pixel_x = int((x - canvas_x1) / canvas_dx)
			pixel_y = int((y - canvas_y1) / canvas_dy)
			if pixel_x >= 0 and pixel_x < img_w \
					and pixel_y >= 0 and pixel_y < img_h:
				k = 1 - img_pixelIndex(pixel_x, pixel_y) / img_colors
				d = (min_width + k * delta) * scale
				path.node[i].d = d
			#else:
			#	k = 0
			#d = (min_width + k * delta) * scale
			#path.node[i].d = d
		return path

	def auto_resolution(self, fX, fY, T):
		p = makePathData(fX, fY, T, res=0.25 / self.scale)
		x, y, w, h = p.boundingRect()
		return max(w, h) * 0.5

	def auto_resolution2(self, fX, fY, T):
		p = makePathData(fX, fY, T, res=0.25 / self.scale)
		l = p.length()
		return l / (T[1] - T[0])

	def append_func(self, fX, fY, T, res=1, color='black', width=3, close_path=False, tolerance=0.0):
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

		# Step 1. Make Path
		pathData = makePathData(fX, fY, T, res / self.scale, close_path)
		if not(pathData):
			return False

		# Step 2. If there is a picture, tracing
		if self.img:
			pathData = self._trace_image(pathData, self.width_range)
			# This must be added the code division ways apart.
			# Convert line to polygon
			path = split(pathData)
			path.strokeToPath()

		# Step 3. Simplification Path
		if tolerance > 0.0:
			#start = time.time()
			for i in range(len(path)):
				path[i] = simplify_points(path[i], tolerance * self.scale)
			#print('simplify_points', time.time() - start)

		# Step 5. Append Path to data
		if len(path[0]) > 0:
			self.data.append(path)
			return True
		else:
			return False

	def plot(self, file_name='plot.svg'):
		""" Saves the file generated <path/> SVG.
		"""
#		if self.grid:                           # if you need a grid, then draw it with a thickness of default and a dark line in the center
#			g = self.grid
#			for i in xrange(g + 1):
#				self._generate_path([[self.x1 + self.dx / g * i, self.y1], \
#									[self.x1 + self.dx / g * i, self.y2]], ['grey', 'lightgrey'][bool(i - g / 2)])
#				self._generate_path([[self.x1, self.y1 + self.dy / g * i], \
#									[self.x2, self.y1 + self.dy / g * i]], ['grey', 'lightgrey'][bool(i - g / 2)])
		header = '<?xml version="1.0" encoding="utf-8"?>\n'
		header += '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="none"\n'
		header += 'width="%i" height="%i" viewBox="%f %f %f %f">\n\t<g fill="%s" fill-rule="evenodd">\n' % \
					(self.w, self.h, self.x1, self.y1, self.dx, self.dy, ['none', 'black'][bool(self.img)])
		footer = "</g>\n</svg>"

		f = open(file_name, 'w')                # write to file
		f.write(header)
		f.write(''.join(reversed([s.asSVG() for s in self.data])))
		f.write(footer)
		f.close()
