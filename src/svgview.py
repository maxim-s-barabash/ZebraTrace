#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2010 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


# This is only needed for Python v2 but is harmless for Python v3.
from PyQt4 import QtCore, QtGui, QtSvg


class SvgView(QtGui.QGraphicsView):
	Native, OpenGL, Image = range(3)

	def __init__(self, parent=None):
		super(SvgView, self).__init__(parent)

		self.renderer = SvgView.Native
		self.svgItem = None
		self.backgroundItem = None
		self.outlineItem = None
		self.image = QtGui.QImage()

		self.setScene(QtGui.QGraphicsScene(self))
		self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
		self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

		# Prepare background check-board pattern.
		tilePixmap = QtGui.QPixmap(32, 32)
		tilePixmap.fill(QtCore.Qt.white)
		tilePainter = QtGui.QPainter(tilePixmap)
		color = QtGui.QColor(192, 192, 192)
		tilePainter.fillRect(0, 0, 16, 16, color)
		tilePainter.fillRect(16, 16, 16, 16, color)
		tilePainter.end()

		self.setBackgroundBrush(QtGui.QBrush(tilePixmap))

	def drawBackground(self, p, rect):
		p.save()
		p.resetTransform()
		p.drawTiledPixmap(self.viewport().rect(),
				self.backgroundBrush().texture())
		p.restore()

	def openFile(self, svg_file):
		if not svg_file.exists():
			return

		s = self.scene()

		if self.backgroundItem:
			drawBackground = self.backgroundItem.isVisible()
		else:
			drawBackground = True

		if self.outlineItem:
			drawOutline = self.outlineItem.isVisible()
		else:
			drawOutline = True

		s.clear()
		self.resetTransform()

		self.svgItem = QtSvg.QGraphicsSvgItem(svg_file.fileName())
		self.svgItem.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
		self.svgItem.setCacheMode(QtGui.QGraphicsItem.NoCache)
		self.svgItem.setZValue(0)

		self.backgroundItem = QtGui.QGraphicsRectItem(self.svgItem.boundingRect())
		self.backgroundItem.setBrush(QtCore.Qt.white)
		self.backgroundItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
		self.backgroundItem.setVisible(drawBackground)
		self.backgroundItem.setZValue(-1)

		self.outlineItem = QtGui.QGraphicsRectItem(self.svgItem.boundingRect())
		outline = QtGui.QPen(QtCore.Qt.darkGray, 1, QtCore.Qt.SolidLine)
		outline.setCosmetic(True)
		self.outlineItem.setPen(outline)
		self.outlineItem.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
		self.outlineItem.setVisible(drawOutline)
		self.outlineItem.setZValue(1)

		s.addItem(self.backgroundItem)
		s.addItem(self.svgItem)
		s.addItem(self.outlineItem)

		s.setSceneRect(self.outlineItem.boundingRect().adjusted(-10, -10, 10, 10))

	def setRenderer(self, renderer):
		self.renderer = renderer

		if self.renderer == SvgView.OpenGL:
			if QtOpenGL.QGLFormat.hasOpenGL():
				self.setViewport(QtOpenGL.QGLWidget(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers)))
		else:
			self.setViewport(QtGui.QWidget())

	def setHighQualityAntialiasing(self, highQualityAntialiasing):
		if QtOpenGL.QGLFormat.hasOpenGL():
			self.setRenderHint(QtGui.QPainter.HighQualityAntialiasing,
					highQualityAntialiasing)

	def setViewBackground(self, enable):
		if self.backgroundItem:
			self.backgroundItem.setVisible(enable)

	def setViewOutline(self, enable):
		if self.outlineItem:
			self.outlineItem.setVisible(enable)

	def paintEvent(self, event):
		if self.renderer == SvgView.Image:
			if self.image.size() != self.viewport().size():
				self.image = QtGui.QImage(self.viewport().size(),
						QtGui.QImage.Format_ARGB32_Premultiplied)

			imagePainter = QtGui.QPainter(self.image)
			QtGui.QGraphicsView.render(self, imagePainter)
			imagePainter.end()

			p = QtGui.QPainter(self.viewport())
			p.drawImage(0, 0, self.image)
		else:
			super(SvgView, self).paintEvent(event)

	def wheelEvent(self, event):
		factor = pow(1.2, event.delta() / 240.0)
		self.scale(factor, factor)
		event.accept()

