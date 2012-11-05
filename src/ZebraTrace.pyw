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
import tempfile
from PyQt4 import QtCore, QtGui, uic
from FuncPlotter2 import FuncPlotter
from svgview import *
from math import *

__version__ = "0.1 alpha"
app_name = "ZebraTRACE"
about = """<center><b>%s</b> version %s. <br><br>
See <a href='http://linuxgraphics.ru/'>linuxgraphics.ru</a>
for more information.<br><br>
Copiright (C) 2012</center>"""


class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		uic.loadUi("mainwindow.ui", self)
		self.tabInfo.hide()
		self.tabColors.hide()

		self.currentPath = ''
		self.tempfilename = os.path.join(tempfile.gettempdir(), "temp.svg")
		self.trace_image = ''
		self.view = SvgView()
		self.horizontalLayoutContainer.addWidget(self.view)
		self.sin = sin
		self.cos = cos
		self.pi = pi
		self.createActions()

	def __del__(self):
		if os.path.isfile(self.tempfilename):
			os.remove(self.tempfilename)

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
			bitmap_file = QtCore.QFile(path)
			if not bitmap_file.exists():
				QtGui.QMessageBox.critical(self, "Open Bitmap File",
					"Could not open file '%s'." % path)
			self.trace_image = path

	def saveFileSVG(self, path=None):
		if not path:
			path = QtGui.QFileDialog.getSaveFileName(self, "Save SVG File",
				self.currentPath, "SVG files (*.svg)")
		if path:
			svg_file = QtCore.QFile(path)
			shutil.copy(self.tempfilename, path)

	def about(self):
		QtGui.QMessageBox.about(self, "About", about % (app_name, __version__))

	def trace(self):
		image_size = [self.spinBoxX.value(), self.spinBoxY.value()]
		dimensions = [-1, -1, 1, 1]
		# количество кривых
		self.n = self.spinBoxCurves.value()
		# диапазон значений переменной
		alpha = [self.doubleSpinBoxAlphaMin.value(),
				self.doubleSpinBoxAlphaMax.value()]
		# качество кривой
		resolution = self.doubleSpinBoxResolution.value()
		# без обводки (при трассировке используется заливка)
		stroke_color = 'none'
		width_range = [self.doubleSpinBoxMin.value(), self.doubleSpinBoxMax.value()]
		funcX = eval("lambda a:" + unicode(self.lineEditX.text()), self.__dict__)
		if self.lineEditY.text() != "":
			funcY = eval("lambda a:" + unicode(self.lineEditY.text()), self.__dict__)
		else:
			funcY = None
		fp = FuncPlotter(image_size, dimensions, trace_image=self.trace_image,
						width_range=width_range)
		self.progressBar.setMaximum(self.n)
		for i in xrange(self.n + 1):
			self.i = float(i)
			fp.append_func(funcX,
							funcY,
							alpha,
							resolution,
							stroke_color,
							close_path=True)
			self.progressBar.setValue(i)
		fp.plot(unicode(self.tempfilename))
		self.view.openFile(QtCore.QFile(self.tempfilename))
		self.progressBar.setValue(0)


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = MainWindow()
	if len(sys.argv) == 2:
		window.openFileBitmap(sys.argv[1])
	else:
		window.openFileBitmap("images/tux.png")
	window.show()
	window.trace()
	sys.exit(app.exec_())
