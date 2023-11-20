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


import os
import sys

from PyQt5.QtGui import QImage

from .path import makePathData, split


# to trace the image is used PyQt4
# (http://www.riverbankcomputing.co.uk/software/pyqt/download)
sys.setswitchinterval(0xfff)


class FuncPlotter:
    def __init__(self, DOM, trace_image=None, width_range=None):
        """Draws the graphics functions.

        Parameters:
        trace_image    - a string specifying the name of the image file to trace
                        or QImage object
        width_range    - a list of two values defining the range of thickness in the trace line
        """
        self.document = DOM
        self.trace_image = trace_image
        self.width_range = width_range
        self.img = None

        if trace_image is None:
            trace_image = DOM.image

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
        scale = self.document.scale

        canvas_x1 = self.document.x1
        canvas_y1 = self.document.y1
        canvas_dx = self.document.dx / img_w
        canvas_dy = self.document.dy / img_h

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
            #    k = 0
            #d = (min_width + k * delta) * scale
            #path.node[i].d = d
        return path

    def auto_resolution(self, fX, fY, T):
        p = makePathData(fX, fY, T, res=0.25 / self.scale)
        _, _, w, h = p.boundingRect()
        return max(w, h) * 0.5

    def auto_resolution2(self, fX, fY, T):
        p = makePathData(fX, fY, T, res=0.25 / self.document.scale)
        l = p.length() if p else 0
        return l / (T[1] - T[0])

    def append_func(self, fX, fY, T, res=1, color='black', width=3, close_path=False):
        """Adds a graph of the functions fX (t) and fY (t).

        fX            - a function of one variable, calculates the coordinates of x or
                        function of the radius of the corner, if the following option (fY) returns False
        fY            - function of one variable that calculates the y-coordinate, or None
        T            - a list of two values ​​defining the range of the variable
        color        - a string that specifies the stroke color of the curve, you can use named values
                        of the SVG specification, or 'none'
        width        - the thickness of the circuit
        close_path    - parameter that indicates whether or not to close the curve
        """

        # Step 1. Make Path
        pathData = makePathData(fX, fY, T, res / self.document.scale, close_path)
        if not(pathData):
            return False

        # Step 2. If there is a picture, tracing
        if self.img:
            pathData = self._trace_image(pathData, self.width_range)
            # This must be added the code division ways apart.
            # Convert line to polygon
            path = split(pathData)
        # Step 3. Append Path to data
        if len(path[0]) > 0:
            self.document.data.append(path)
            return True
        else:
            return False
