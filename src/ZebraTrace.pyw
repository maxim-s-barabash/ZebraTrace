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


import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
import os
import shutil
import mainwindow_rc
import time
from PyQt4 import QtCore, QtGui, uic
from funcplotter2 import FuncPlotter
from svgview import *
from app_config import *
from math import *


about = """<center><b>%s</b> version %s. <br><br>
See <a href='http://linuxgraphics.ru/'>linuxgraphics.ru</a>
for more information.<br><br>
Copyright (C) 2012</center>"""


class Function():
	def __init__(self, func=None):
		self.setFunc(func)

	def setFunc(self, func):
			self.func = func.strip()

	def getFunc(self, cfg):
		if self.func:
			ret = eval("lambda a:" + self.func, cfg)
		else:
			ret = None
		return ret


class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		uic.loadUi("mainwindow.ui", self)
		self.currentPath = ''
		self.trace_image = ''

		self.app_data = AppData()

		self.view = SvgView()
		self.horizontalLayoutContainer.addWidget(self.view)
		self.createActions()

	def __del__(self):
		if os.path.isfile(self.app_data.temp_svg):
			os.remove(self.app_data.temp_svg)

	def createActions(self):
		self.actionOpenBitmap.triggered.connect(self.openFileBitmap)
		self.actionSaveSVG.triggered.connect(self.saveFileSVG)
		self.actionQuit.triggered.connect(QtGui.qApp.quit)
		self.actionAbout.triggered.connect(self.about)
		self.actionAboutQt.triggered.connect(QtGui.qApp.aboutQt)
		self.connect(self.pushButtonTrace,
					QtCore.SIGNAL("clicked()"), self.trace)
		self.connect(self.pushButtonSaveSVG,
					QtCore.SIGNAL("clicked()"), self.saveFileSVG)
		self.connect(self.pushButtonQuit,
					QtCore.SIGNAL("clicked()"), self.close)

	def openFileBitmap(self, path=None):
		if not path:
			path = QtGui.QFileDialog.getOpenFileName(self, "Open Bitmap File",
				self.currentPath, "Bitmap files (*.jpg *.ipeg *.png)")
		if path:
			self.trace_image = unicode(path)
			self.currentPath = os.path.dirname(self.trace_image)
			self.trace()

	def saveFileSVG(self, path=None):
		if not path:
			path = QtGui.QFileDialog.getSaveFileName(self, "Save SVG File",
				self.currentPath, "SVG files (*.svg)")
		if path:
			svg_file = unicode(path)
			self.currentPath = os.path.dirname(svg_file)
			shutil.copy(self.app_data.temp_svg, svg_file)

	def about(self):
		QtGui.QMessageBox.about(self, "About", about % (self.app_data.app_name, 
														self.app_data.app_version))

	def trace(self):
		image_size = [self.spinBoxX.value(), self.spinBoxY.value()]
		dimensions = [-1, -1, 1, 1]
		# number of curves
		n = self.spinBoxCurves.value()
		# range of the variable
		alpha = [self.doubleSpinBoxAlphaMin.value(),
				self.doubleSpinBoxAlphaMax.value()]
		# curve quality
		resolution = self.doubleSpinBoxResolution.value()
		# no stroke (when tracing is used fill)
		stroke_color = 'none'
		width_range = [self.doubleSpinBoxMin.value(), self.doubleSpinBoxMax.value()]

		dic = {"sin": sin,
				"cos": cos,
				"pi": pi,
				"n": n,
			}

		funcX = Function(unicode(self.lineEditX.text())).getFunc(dic)
		funcY = Function(unicode(self.lineEditY.text())).getFunc(dic)

		fp = FuncPlotter(image_size, dimensions, trace_image=self.trace_image,
						width_range=width_range)

		self.progressBar.setMaximum(n + 1)
		start = time.time()

		for i in xrange(n + 1):
			dic['i'] = float(i)
			fp.append_func(funcX,
							funcY,
							alpha,
							resolution,
							stroke_color,
							close_path=True)
			self.progressBar.setValue(i)

		fp.plot(self.app_data.temp_svg)
		print "- Done in", time.time() - start, 'seconds.'
		self.view.openFile(QtCore.QFile(self.app_data.temp_svg))
		self.progressBar.setValue(0)


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = MainWindow()
	if len(sys.argv) == 2:
		window.openFileBitmap(sys.argv[1])
	else:
		window.openFileBitmap("images/tux.png")
	window.show()
	#window.trace()
	sys.exit(app.exec_())
