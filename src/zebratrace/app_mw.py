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


import os

from PyQt4 import QtCore, QtGui

from . import event
from .gui.ui_mainwindow import Ui_MainWindow
from .gui.widgets.svgview import TraceCanvas
from .utils import UNITS, pxToUnit, unitToPx, unitToUnit, unicode


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, app):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        self.app = app
        self.config = app.config

        self.view = TraceCanvas()
        self.createActions()
        self.progressBar.setMaximum(100)
        self.tabPreferences.setCurrentIndex(0)
        self.topPanel.setEnabled(False)
        self.buttonTrace.setEnabled(False)
        self.buttonSave.setEnabled(False)
        self.actionSaveAs.setEnabled(False)
        self.sliderTransparency.setEnabled(False)
        self.viewContainer.addWidget(self.view)
        self.feedback()

    def closeEvent(self, e):
        self.configUpdate()
        self.app.quit()

    def keyPressEvent(self, e):
        if type(e) == QtGui.QKeyEvent:
            if (e.key() == QtCore.Qt.Key_Escape):
                event.CANCEL = True
            e.accept()
        else:
            e.ignore()

    def createActions(self):
        app = self.app
        self.actionOpenBitmap.triggered.connect(app.open)
        self.actionSaveAs.triggered.connect(app.saveAs)
        self.actionSavePreset.triggered.connect(app.savePreset)
        self.actionLoadPreset.triggered.connect(app.loadPreset)
        self.actionQuit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(app.about)
        self.actionAboutQt.triggered.connect(app.aboutQt)

        self.buttonAutoTrace.toggled.connect(app.autoTrace)
        self.buttonTrace.clicked.connect(app.trace)
        self.buttonSave.clicked.connect(app.saveAs)
        self.buttonHelp.clicked.connect(app.help)

        self.actionBackground.toggled.connect(self.view.setViewBackground)
        self.actionBorder.toggled.connect(self.view.setViewOutline)
        self.sliderTransparency.valueChanged.connect(self.view.setOpacity)
        self.previewMode.currentIndexChanged.connect(self.sliderTransparency.setEnabled)
        self.previewMode.currentIndexChanged.connect(self.view.setViewTraceImage)
        self.previewMode.currentIndexChanged.connect(self.labelTransparency.setEnabled)

        self.units.currentIndexChanged.connect(self.unitsChanged)
        self.docResolution.valueChanged.connect(self.docResolutionChanged)
        self.docResolution.valueChanged.connect(self.app.docClean)
        self.view.mouseMoveEvent = self.viewMouseMove

        self.numberCurves.valueChanged.connect(self.app.docClean)
        self.curveWidthMin.valueChanged.connect(self.app.docClean)
        self.curveWidthMax.valueChanged.connect(self.app.docClean)
        self.nodeReduction.valueChanged.connect(self.app.docFlatClean)
        self.curveWriting.currentIndexChanged.connect(self.app.docFlatClean)
        self.resolution.valueChanged.connect(self.app.docClean)
        self.rangeMin.valueChanged.connect(self.app.docClean)
        self.rangeMax.valueChanged.connect(self.app.docClean)

        self.coordSystem.currentIndexChanged.connect(self.app.docClean)
        self.lineEditX.textChanged.connect(self.app.docClean)
        self.lineEditY.textChanged.connect(self.app.docClean)

        event.connect(event.CONFIG_LOADED, self.configLoaded)
        event.connect(event.CONFIG_LOADED, self.app.trace)
        event.connect(event.DOC_OPENED, self.open)
        event.connect(event.DOC_OPENED, self.windowTitleChanged)
        event.connect(event.CONFIG_CHANGED, self.windowTitleChanged)

        event.connect(event.DOC_TRACE, self.traceBegin)
        event.connect(event.DOC_MODIFIED, self.infoUpdated)
        event.connect(event.DOC_MODIFIED, self.traceEnd)

        event.connect(event.APP_STATUS, self.feedback)

    def configLoaded(self):
        config = self.config
        dpi = config.dpi
        units = config.units

        self.numberCurves.setValue(config.numberCurves)

        self.curveWidthMin.setValue(pxToUnit(config.curveWidthMin, units, dpi))
        self.curveWidthMax.setValue(pxToUnit(config.curveWidthMax, units, dpi))

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

        self.units.setCurrentIndex(units)
        self.previewMode.setCurrentIndex(config.previewMode)
        self.docResolution.setValue(dpi)

    def configUpdate(self, cnf=None):
        if cnf is None:
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
                   "funcY": unicode(self.lineEditY.text()),

                   "sliderTransparency": self.sliderTransparency.value(),
                   "boxAdvancedPref": self.boxAdvancedPref.isChecked(),
                   "units": units,
                   "previewMode": self.previewMode.currentIndex(),
                   "dpi": self.docResolution.value()
                   }
        self.config.update(cnf)

    def unitsChanged(self, units):
        config = self.config
        w = unitToUnit(self.curveWidthMin.value(), config.units, units, config.dpi)
        self.curveWidthMin.setValue(w)
        w = unitToUnit(self.curveWidthMax.value(), config.units, units, config.dpi)
        self.curveWidthMax.setValue(w)
        self.config.units = units

    def docResolutionChanged(self, val):
        self.config.dpi = val

    def windowTitleChanged(self):
        if self.app.document is not None:
            dpi = self.config.dpi
            units = self.config.units
            img_w = pxToUnit(self.app.document.w, units, dpi)
            img_h = pxToUnit(self.app.document.h, units, dpi)
            basename = os.path.basename(self.app.document.image_fn)
            title = "%s - %s [%ix%i %s]" % (self.app.app_name, basename, img_w, img_h, UNITS[units])
        else:
            title = "%s - %s" % (self.app.app_name, self.app.app_version)

        self.setWindowTitle(title)

    def infoUpdated(self):
        doc = self.app.document
        info = doc.info

        trace_elapsed = info.get('trace_end', 0) - info.get('trace_start', 0)
        flatten_paths = info.get('flatten_paths_end', 0) - info.get('flatten_paths_start', 0)
        number_object = len(doc.flat_data)
        number_nodes = 0
        for i in doc.flat_data:
            for j in i:
                number_nodes += len(j)

        text = unicode(self.tr("Time trace: %5.3f seconds.\n")) % trace_elapsed
        text += unicode(self.tr("Time flatten paths: %5.3f seconds.\n")) % flatten_paths
        text += unicode(self.tr("Graphic Objects\n  Number of objects: %i\n  Number of nodes: %i\n")) % (number_object, number_nodes)

        self.infoText.setPlainText(text)
        self.labelNumberObject.setText(unicode(number_object))
        self.labelNumberNodes.setText(unicode(number_nodes))

    def viewMouseMove(self, e):
        super(TraceCanvas, self.view).mouseMoveEvent(e)
        pos = self.view.mapToScene(e.pos())
        x = pxToUnit(pos.x(), self.config.units, self.config.dpi)
        y = pxToUnit(pos.y(), self.config.units, self.config.dpi)
        self.labelPos.setText('(%4.3f;%4.3f)' % (x, y))

    def feedback(self, text='', progress=0, **kw):
        self.labelFeedback.setText(text)
        self.progressBar.setValue(int(progress))
        self.app.processEvents()

    def traceBegin(self):
        self.configUpdate()
        self.buttonAutoTrace.setEnabled(False)
        self.buttonTrace.setEnabled(False)
        self.buttonSave.setEnabled(False)
        self.actionSaveAs.setEnabled(False)

    def traceEnd(self):
        self.view.openFileSVG(QtCore.QFile(self.app.temp_svg))
        self.view.setFocus(True)
        self.buttonAutoTrace.setEnabled(True)
        self.buttonTrace.setEnabled(True)
        self.buttonSave.setEnabled(True)
        self.actionSaveAs.setEnabled(True)
        self.feedback()

    def open(self):
        self.view.openFileIMG(self.app.document.image)
        self.view.resetTransform()
        self.previewMode.setCurrentIndex(1)
        self.buttonTrace.setEnabled(True)
        self.buttonSave.setEnabled(False)
        self.actionSaveAs.setEnabled(False)
        self.topPanel.setEnabled(True)
