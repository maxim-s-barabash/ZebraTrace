#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright 2012 Maxim.S.Barabash <maxim.s.barabash@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import shutil
import time
from math import cos, sin

from PyQt4 import QtCore, QtGui
from .gui.widgets.svgview import *
from .gui.ui_mainwindow import Ui_MainWindow

from .geom.funcplotter2 import FuncPlotter
from .geom.function import Function
from .geom.image import desaterate, grayscale
from .geom.DOM import DOM

from .app_config import Preset
from .utils import *

from .utils import format_svg
from .utils import format_gcode
from .utils import format_eps



# FIXME move to class Info to funcplotter2
class Info(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.clean()

    def clean(self):
        self.traceTime = 0.0
        self.numberObject = 0
        self.numberNodes = 0

    def __setattr__(self, attr, value):
        if not hasattr(self, attr) or getattr(self, attr) != value:
            self.__dict__[attr] = value
            self.emit(QtCore.SIGNAL("infoChanget()"))

    def __call__(self):
        text = ''
        text += unicode(self.tr("Time trace: %5.3f seconds.\n")) % self.traceTime
        text += unicode(self.tr("Graphic Objects\n  Number of objects: %i\n  Number of nodes: %i\n")) % (self.numberObject, self.numberNodes)
        return text


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, data, config):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        self.app_data = data
        self.config = config
        self.info = Info()


        self.trace_image = ""
        self.image = None

#        self.image_size = [1000, 1000]
#        self.dimensions = [-1, -1, 1, 1]

        self.document = None
        
        self.Escape = False

        self.view = TraceCanvas()
        self.createActions()

        self.tabPreferences.setCurrentIndex(0)
        self.topPanel.setEnabled(False)
        self.buttonTrace.setEnabled(False)
        self.buttonSave.setEnabled(False)
        self.actionSaveAs.setEnabled(False)
        self.sliderTransparency.setEnabled(False)
        self.viewContainer.addWidget(self.view)
        self.loadConfig(self.app_data.app_config)
        self.windowTitleChanged()
        self.feedback()

    def __del__(self):
        import os
        self.saveConfig(self.app_data.app_config)
        if os.path.isfile(self.app_data.temp_svg):
            os.remove(self.app_data.temp_svg)

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            if (event.key() == QtCore.Qt.Key_Escape):
                self.Escape = True
            event.accept()
        else:
            event.ignore()

    def createActions(self):
        self.actionOpenBitmap.triggered.connect(self.openFileBitmap)
        self.actionSaveAs.triggered.connect(self.saveFileAs)
        self.actionSavePreset.triggered.connect(self.savePreset)
        self.actionLoadPreset.triggered.connect(self.loadPreset)
        self.actionQuit.triggered.connect(QtGui.qApp.quit)
        self.actionAbout.triggered.connect(self.about)
        self.actionAboutQt.triggered.connect(QtGui.qApp.aboutQt)
        self.connect(self.buttonTrace,
                    QtCore.SIGNAL("clicked()"), self.trace)
        self.connect(self.buttonSave,
                    QtCore.SIGNAL("clicked()"), self.saveFileAs)
        self.connect(self.buttonHelp,
                    QtCore.SIGNAL("clicked()"), self.help)

        self.connect(self,
                    QtCore.SIGNAL("loadPreset()"), self.trace)
#        self.connect(self,
#                    QtCore.SIGNAL("openFileBitmap()"), self.trace)
        self.connect(self.info,
                    QtCore.SIGNAL("infoChanget()"), self.infoUpdate)

        self.actionBackground.toggled.connect(self.view.setViewBackground)
        self.actionBorder.toggled.connect(self.view.setViewOutline)
        self.sliderTransparency.valueChanged.connect(self.view.setOpacity)
        self.previewMode.currentIndexChanged.connect(self.sliderTransparency.setEnabled)
        self.previewMode.currentIndexChanged.connect(self.view.setViewTraceImage)
        self.previewMode.currentIndexChanged.connect(self.labelTransparency.setEnabled)

        self.units.currentIndexChanged.connect(self.unitsChanged)
        self.docResolution.valueChanged.connect(self.docResolutionChanged)
#        self.view.scene.mouseMoveEvent.connect(self.viewMouseMove)
        self.view.mouseMoveEvent = self.viewMouseMove
        self.view.mouseMoveEvent = self.viewMouseMove


        self.info.clean()

    def openFileBitmap(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open Bitmap File"),
                unicode(self.config.currentPath),
                self.tr("Bitmap files (*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tga);;All files (*.*)"))
        if path:
            trace_image = unicode(path)
            self.config.currentPath = unicode(os.path.dirname(trace_image))
            
            img = QtGui.QImage(trace_image)
            
            img_w = float(img.width())
            img_h = float(img.height())
            self.image_size = [img_w, img_h]
            if img_w == 0:
                QtGui.QMessageBox.warning(self, self.tr("Open file"),
                    self.tr("This file is corrupt or not supported?"))
                return

            self.document = DOM(self.image_size)

            self.trace_image = trace_image

            self.progressBar.setMaximum(100)
            img = desaterate(img, self.feedback)
            self.image = grayscale(img)
            self.view.openFileIMG(self.image)

            self.view.resetTransform()
            self.topPanel.setEnabled(True)

            self.windowTitleChanged()
            self.previewMode.setCurrentIndex(1)
            self.buttonTrace.setEnabled(True)
            self.buttonSave.setEnabled(False)
            self.actionSaveAs.setEnabled(False)
            self.emit(QtCore.SIGNAL("openFileBitmap()"))

    def saveFileAs(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save File"),
                unicode(self.config.currentPath), self.tr("SVG files (*.svg);;NGC g-code files (*.ngc);;EPS files (*.eps)"))
            print(path)
        if path:
            filename = unicode(path)
            root, ext = os.path.splitext(filename)
            ext = unicode(ext.upper())
            self.config.currentPath = unicode(os.path.dirname(filename))
            print(ext)
            if ext == '.SVG':
                shutil.copy(self.app_data.temp_svg, filename)
            elif ext == '.NGC':
                G = format_gcode.GCode(self.document)
                G.save(filename)
            elif ext == '.EPS':
                G = format_eps.EPS(self.document)
                G.save(filename)

    def loadPreset(self, path=None):
        if not path:
            presetPath = self.config.presetPath or self.app_data.preset_dir
            path = QtGui.QFileDialog.getOpenFileName(self, self.tr("Load Preset File"),
                unicode(presetPath), self.tr("Preset files (*.preset)"))
        if path:
            preset_file = unicode(path)
            self.config.presetPath = unicode(os.path.dirname(preset_file))
            preset = Preset()
            preset.load(preset_file)
            self.resolution.setValue(preset.resolution * 100.0)
            self.lineEditX.setText(unicode(preset.funcX))
            self.lineEditY.setText(unicode(preset.funcY))
            self.rangeMin.setValue(preset.rangeMin)
            self.rangeMax.setValue(preset.rangeMax)
            self.coordSystem.setCurrentIndex(preset.polar)
            self.emit(QtCore.SIGNAL("loadPreset()"))

    def savePreset(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save Preset File"),
                unicode(self.config.presetPath), self.tr("Preset files (*.preset)"))
        if path:
            preset_file = unicode(path)
            self.config.presetPath = unicode(os.path.dirname(preset_file))
            preset = Preset()
            preset.resolution = self.resolution.value() / 100.0
            preset.funcX = unicode(self.lineEditX.text())
            preset.funcY = unicode(self.lineEditY.text())
            preset.rangeMin = self.rangeMin.value()
            preset.rangeMax = self.rangeMax.value()
            preset.polar = self.coordSystem.currentIndex()
            preset.save(preset_file)

    def loadConfig(self, path=None):
        self.config.load(path)
        config = self.config
        units = config.units

        self.numberCurves.setValue(config.numberCurves)
        
        self.curveWidthMin.setValue(pxToUnit(config.curveWidthMin, units))
        self.curveWidthMax.setValue(pxToUnit(config.curveWidthMax, units))
        
        self.nodeReduction.setValue(config.nodeReduction)
        self.curveWriting.setCurrentIndex(config.curveWriting)

        self.resolution.setValue(config.resolution * 100.0)
        self.lineEditX.setText(unicode(config.funcX))
        self.lineEditY.setText(unicode(config.funcY))
        self.rangeMin.setValue(config.rangeMin)
        self.rangeMax.setValue(config.rangeMax)
        self.coordSystem.setCurrentIndex(config.polar)

        self.sliderTransparency.setValue(config.sliderTransparency)
        self.boxAdvancedPref.setChecked(config.boxAdvancedPref)
        
        self.units.setCurrentIndex(config.units)
        self.previewMode.setCurrentIndex(config.previewMode)
        self.docResolution.setValue(config.dpi)

    def configUpdate(self, cnf=None):
        if cnf == None:
            units = self.units.currentIndex()
            dpi = self.docResolution.value()
            cnf = {"numberCurves": self.numberCurves.value(),
            
            "curveWidthMin": unitToPx(self.curveWidthMin.value(), units, dpi),
            "curveWidthMax": unitToPx(self.curveWidthMax.value(), units, dpi),
            
            "nodeReduction": self.nodeReduction.value(),
            "curveWriting": self.curveWriting.currentIndex(),

            "resolution": self.resolution.value() / 100.0,
            "rangeMin": self.rangeMin.value(),
            "rangeMax": self.rangeMax.value(),
            "polar": self.coordSystem.currentIndex(),
            "funcX": unicode(self.lineEditX.text()),
            "funcY":  unicode(self.lineEditY.text()),

            "sliderTransparency": self.sliderTransparency.value(),
            "boxAdvancedPref": self.boxAdvancedPref.isChecked(),
            "units": units,
            "previewMode": self.previewMode.currentIndex(),
            "dpi": self.docResolution.value()
            }
        self.config.update(cnf)

    def saveConfig(self, path=None):
        if path is None:
            path = self.app_data.app_config
        self.configUpdate()
        self.config.save(path)

    def unitsChanged(self):
        units = self.units.currentIndex()

        self.curveWidthMin.setValue(unitToUnit(self.curveWidthMin.value(), 
                    self.config.units, units, self.config.dpi))
        self.curveWidthMax.setValue(unitToUnit(self.curveWidthMax.value(), 
                    self.config.units, units, self.config.dpi))
        self.config.units = units
        self.windowTitleChanged()

    def docResolutionChanged(self):
        self.config.dpi = self.docResolution.value()
        self.windowTitleChanged()

    def windowTitleChanged(self):
        if self.document is None:
            self.setWindowTitle("%s" % self.app_data.app_name)
        else:
            img_w = pxToUnit(self.document.w, self.config.units, self.config.dpi)
            img_h = pxToUnit(self.document.h, self.config.units, self.config.dpi)
            self.setWindowTitle("%s - %s [%ix%i %s]" % (self.app_data.app_name,
                                    os.path.basename(self.trace_image), img_w, img_h,
                                    UNITS[self.config.units]))

    def help(self):
        import webbrowser
        url = self.app_data.help_index
        webbrowser.open(url)

    def infoUpdate(self):
        self.infoText.setPlainText(self.info())
        self.labelNumberObject.setText(unicode(self.info.numberObject))
        self.labelNumberNodes.setText(unicode(self.info.numberNodes))

    def about(self):
        about = unicode(self.tr("""<center><b>%s</b> version %s. <br><br>
See <a href="http://maxim-s-barabash.github.io/ZebraTrace/">ZebraTrace</a>
for more information.<br><br>
Copyright (C) 2012-2014</center>"""))
        QtGui.QMessageBox.about(self, self.tr("About"), about % (self.app_data.app_name,
                                                        self.app_data.app_version))

    def viewMouseMove(self, event):
        super(TraceCanvas, self.view).mouseMoveEvent(event)
        pos = self.view.mapToScene(event.pos())
        x = pxToUnit(pos.x(), self.config.units, self.config.dpi)
        y = pxToUnit(pos.y(), self.config.units, self.config.dpi)
        self.labelPos.setText('(%4.3f;%4.3f)' % (x,y))

    def feedback(self, text='', progress=0):
        if text == '' and progress == 0:
            self.Escape = False
            
        if text is not None:
            self.labelFeedback.setText(text)
        if progress is not None:
            self.progressBar.setValue(progress)
        QtGui.QApplication.processEvents()
        
        # print(not self.Escape)
        return(not self.Escape)


    def trace(self):
        if not(self.buttonTrace.isEnabled()):
            return
        self.info.clean()
        self.document.clean()
        self.saveConfig()

        self.buttonTrace.setEnabled(False)
        self.buttonSave.setEnabled(False)
        self.actionSaveAs.setEnabled(False)

        config = self.config

        n = config.numberCurves                            # number of curves
        alpha = [config.rangeMin, config.rangeMax]        # range of the variable
        resolution = config.resolution                    # curve quality
        stroke_color = "none"                            # no stroke (when tracing is used fill)
        width_range = [config.curveWidthMin, config.curveWidthMax]
        tolerance = config.nodeReduction / 100.
        funcX = Function(config.funcX)
        funcY = Function(config.funcY)
        curveWriting = config.curveWriting

        polar_coord = self.coordSystem.currentIndex()

        fp = FuncPlotter(self.document, trace_image=self.image,
                        width_range=width_range)


        dprogres = 100.0 / n

        # Step 1. Make Path
        start = time.time()
        msg = self.tr('Trace the Image. Press ESC to Cancel.')
        for i in xrange(1, n + 1):
            if self.feedback(text=msg, progress = i * dprogres):
                try:
                    fX = funcX({'i': float(i), 'n': float(n)})
                    fY = funcY({'i': float(i), 'n': float(n)})
                    if polar_coord and fY:
                        fR, fT = fX, fY
                        fX = lambda a: fR(a) * cos(fT(a))
                        fY = lambda a: fR(a) * sin(fT(a))
                    elif not fY:                            # If only the function x
                        fR = fX                             # then consider the polar coordinates
                        fX = lambda a: fR(a) * cos(a)
                        fY = lambda a: fR(a) * sin(a)

                    ##auto_resolution = fp.auto_resolution(fX, fY, alpha)
                    auto_resolution = fp.auto_resolution2(fX, fY, alpha)
                except (SyntaxError, TypeError, NameError, ZeroDivisionError):
                    err = sys.exc_info()[1]
                    QtGui.QMessageBox.critical(self, self.tr("Error in function"),
                        unicode(err))
                    break


                if fp.append_func(fX,
                                fY,
                                alpha,
                                resolution * auto_resolution,
                                stroke_color,
                                close_path=True,
                                tolerance=tolerance,
                                writing=curveWriting,
                                ):
                    self.info.numberObject = len(fp.document.data)
                    self.info.numberNodes += fp.document.data[-1].countNodes()
            else:
                break


        QtGui.QApplication.processEvents()
        
        self.info.traceTime = time.time() - start
        ########################################
        SIMPLIFICATION = 1

        if SIMPLIFICATION == 0:
            # Douglas-Peucker line simplification.
            from .geom.dp import simplify_points
        else:
            # Visvalingam line simplification.
            from .geom.visvalingam import simplify_visvalingam_whyatt as simplify_points
        
        prev = self.document
        self.info.numberNodes =self.info.numberNodes * 2
        for path in prev:
            path.strokeToPath(curveWriting)
            if tolerance > 0.0:
                tempCountNodes = path.countNodes()
                
                for i in range(len(path)):
                    path[i].node = simplify_points(path[i].node, tolerance * prev.scale)
                
                self.info.numberObject = len(fp.document.data)
                self.info.numberNodes -= (tempCountNodes - path.countNodes())
                self.feedback(text=self.tr('Simplify Points'))

        previewSVG = format_svg.SVG(prev, feedback=self.feedback)
        previewSVG.save(self.app_data.temp_svg)
        #########################################

        self.view.openFileSVG(QtCore.QFile(self.app_data.temp_svg))
        self.feedback()

        self.buttonTrace.setEnabled(True)
        self.view.setFocus(True)
        self.buttonSave.setEnabled(True)
        self.actionSaveAs.setEnabled(True)
