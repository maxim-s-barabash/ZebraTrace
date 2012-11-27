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
sys.setdefaultencoding("UTF-8")
import os
import shutil
import gui.mainwindow_rc
import time
from PyQt4 import QtCore, QtGui, uic
from funcplotter2 import FuncPlotter
from widgets.svgview import *
from app_config import *
from math import *


about = """<center><b>%s</b> version %s. <br><br>
See <a href="http://linuxgraphics.ru/">linuxgraphics.ru</a>
for more information.<br><br>
Copyright (C) 2012</center>"""

info = """Time trace: %5.3f seconds.
Graphic Objects
  Number of objects: %i
  Number of points: %i
"""


class Function():
	def __init__(self, func=None):
		self.setFunc(func)
		self.dic = {"sin": sin,
				"cos": cos,
				"tan": tan,
				"sqrt": sqrt,
				"pi": pi,
				"i": 0,
				"n": 0,
				}

	def setFunc(self, func):
			self.func = func.strip()

	def __call__(self, cfg={}):
		if self.func:
			dic = self.dic
			dic.update(cfg)
			ret = eval("lambda a:" + self.func, dic)
		else:
			ret = None
		return ret


# FIXME move to class Info to funcplotter2
class Info(QtCore.QObject):
	def __init__(self):
		QtCore.QObject.__init__(self)
		self.clear()

	def clear(self):
		self.traceTime = 0.0
		self.numberObject = 0
		self.numberPoint = 0

	def __setattr__(self, attr, value):
		if not hasattr(self, attr) or getattr(self, attr) != value:
			self.__dict__[attr] = value
			self.emit(QtCore.SIGNAL("infoChanget()"))

	def __call__(self):
		text = info % (self.traceTime,
						self.numberObject,
						self.numberPoint)
		return text


class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		uic.loadUi("gui/mainwindow.ui", self)
		self.currentPath = ""
		self.presetPath = "./preset/"
		self.trace_image = ""
		self.app_data = AppData()
		self.config = AppConfig()
		self.info = Info()

		self.loadConfig(self.app_data.app_config)
		self.loadPreset("./preset/default.preset")

		self.view = SvgView()
		self.tabProperties.setCurrentIndex(0)
		self.PreviewMode.setEnabled(False)
		self.viewContainer.addWidget(self.view)

		self.createActions()

	def __del__(self):
		self.saveConfig(self.app_data.app_config)
		if os.path.isfile(self.app_data.temp_svg):
			os.remove(self.app_data.temp_svg)

	def createActions(self):
		self.actionOpenBitmap.triggered.connect(self.openFileBitmap)
		self.actionSaveSVG.triggered.connect(self.saveFileSVG)
		self.actionSavePreset.triggered.connect(self.savePreset)
		self.actionLoadPreset.triggered.connect(self.loadPreset)
		self.actionQuit.triggered.connect(QtGui.qApp.quit)
		self.actionAbout.triggered.connect(self.about)
		self.actionAboutQt.triggered.connect(QtGui.qApp.aboutQt)
		self.connect(self.buttonTrace,
					QtCore.SIGNAL("clicked()"), self.trace)
		self.connect(self.buttonSaveSVG,
					QtCore.SIGNAL("clicked()"), self.saveFileSVG)
		self.connect(self.buttonQuit,
					QtCore.SIGNAL("clicked()"), self.close)

		self.connect(self,
					QtCore.SIGNAL("loadPreset()"), self.trace)
		self.connect(self,
					QtCore.SIGNAL("openFileBitmap()"), self.trace)
		self.connect(self.info,
					QtCore.SIGNAL("infoChanget()"), self.infoUpdate)

		self.actionBackground.toggled.connect(self.view.setViewBackground)
		self.actionBorder.toggled.connect(self.view.setViewOutline)

	def openFileBitmap(self, path=None):
		if not path:
			path = QtGui.QFileDialog.getOpenFileName(self, "Open Bitmap File",
				self.currentPath, "Bitmap files (*.jpg *.ipeg *.png *.gif *.tiff)")
		if path:
			self.trace_image = unicode(path)
			self.currentPath = os.path.dirname(self.trace_image)
			self.view.resetTransform()
			self.emit(QtCore.SIGNAL("openFileBitmap()"))

	def saveFileSVG(self, path=None):
		if not path:
			path = QtGui.QFileDialog.getSaveFileName(self, "Save SVG File",
				self.currentPath, "SVG files (*.svg)")
		if path:
			svg_file = unicode(path)
			self.currentPath = os.path.dirname(svg_file)
			shutil.copy(self.app_data.temp_svg, svg_file)

	def loadPreset(self, path=None):
		if not path:
			path = QtGui.QFileDialog.getOpenFileName(self, "Load Preset File",
				self.presetPath, "Preset files (*.preset)")
		if path:
			preset_file = unicode(path)
			self.presetPath = os.path.dirname(preset_file)
			preset = Preset()
			preset.load(preset_file)
			self.lineEditX.setText(preset.funcX)
			self.lineEditY.setText(preset.funcY)
			self.rangeMin.setValue(preset.rangeMin)
			self.rangeMax.setValue(preset.rangeMax)
			self.emit(QtCore.SIGNAL("loadPreset()"))

	def savePreset(self, path=None):
		if not path:
			path = QtGui.QFileDialog.getSaveFileName(self, "Save Preset File",
				self.presetPath, "Preset files (*.preset)")
		if path:
			preset_file = unicode(path)
			self.presetPath = os.path.dirname(preset_file)
			preset = Preset()
			preset.funcX = unicode(self.lineEditX.text())
			preset.funcY = unicode(self.lineEditY.text())
			preset.rangeMin = self.rangeMin.value()
			preset.rangeMax = self.rangeMax.value()
			preset.save(preset_file)

	def loadConfig(self, path=None):
		self.config.load(path)
		config = self.config
		self.numberCurves.setValue(config.numberCurves)
		self.curveResolution.setValue(config.curveResolution)
		self.curveWidthMin.setValue(config.curveWidthMin)
		self.curveWidthMax.setValue(config.curveWidthMax)
		self.nodeReduction.setValue(config.nodeReduction)

	def configUpdate(self, cnf=None):
		if cnf == None:
			cnf = {"numberCurves": self.numberCurves.value(),
			"curveResolution": self.curveResolution.value(),
			"curveWidthMin": self.curveWidthMin.value(),
			"curveWidthMax": self.curveWidthMax.value(),
			"nodeReduction": self.nodeReduction.value(),
			}
		self.config.update(cnf)

	def saveConfig(self, path=None):
		self.configUpdate()
		self.config.save(path)

	def infoUpdate(self):
		self.infoText.setPlainText(self.info())

	def about(self):
		QtGui.QMessageBox.about(self, "About", about % (self.app_data.app_name,
														self.app_data.app_version))

	def trace(self):
		self.info.clear()
		img = QtGui.QImage(self.trace_image)
		img_w = float(img.width())
		img_h = float(img.height())
		img_d = [[1, img_w / img_h], [img_h / img_w, 1]][img_w > img_h]
		image_size = [img_w, img_h]
		dimensions = [-1 * img_d[1], -1 * img_d[0], 1 * img_d[1], 1 * img_d[0]]
		# number of curves
		n = self.numberCurves.value()
		# range of the variable
		alpha = [self.rangeMin.value(), self.rangeMax.value()]
		# curve quality
		resolution = self.curveResolution.value()
		# no stroke (when tracing is used fill)
		stroke_color = "none"
		width_range = [self.curveWidthMin.value(), self.curveWidthMax.value()]
		tolerance = self.nodeReduction.value() / 10000.

		funcX = Function(unicode(self.lineEditX.text()))
		funcY = Function(unicode(self.lineEditY.text()))

		fp = FuncPlotter(image_size, dimensions, trace_image=self.trace_image,
						width_range=width_range)

		self.progressBar.setMaximum(n + 1)
		start = time.time()

		for i in xrange(1, n + 1):
			fp.append_func(funcX({'i': float(i), 'n': n}),
							funcY({'i': float(i), 'n': n}),
							alpha,
							resolution,
							stroke_color,
							close_path=True,
							tolerance=tolerance)
			self.info.numberPoint += len(fp.coords) - 1
			self.info.numberObject += 1
			self.info.traceTime = time.time() - start

			QtGui.QApplication.processEvents()
			self.progressBar.setValue(i)

		fp.plot(self.app_data.temp_svg)

		self.info.traceTime = time.time() - start

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
