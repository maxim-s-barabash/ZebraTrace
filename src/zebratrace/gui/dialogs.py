# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

tr = lambda a: a


def about(mw):
        about = mw.tr("""<center><b>%s</b> version %s.<br><br>
See <a href="http://maxim-s-barabash.github.io/ZebraTrace/">ZebraTrace</a>
for more information.<br><br>
Copyright (C) 2012-2015</center>""")
        about = str(about) % (mw.app.app_name, mw.app.app_version)
        QtGui.QMessageBox.about(mw, mw.tr("About"), about)


def getBitmapFileName(mw, path):
    filters = mw.tr("Bitmap files (*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tga);;All files (*.*)")
    fn = QtGui.QFileDialog.getOpenFileName(mw, mw.tr("Open Bitmap File"),
                                           path, filters)
    return fn


def getSaveFileName(mw, path):
    filters = mw.tr("SVG files (*.svg);;NGC g-code files (*.ngc);;EPS files (*.eps)")
    fn = QtGui.QFileDialog.getSaveFileName(mw, mw.tr("Save File"),
                                           path, filters)
    return fn


def getPresetName(mw, path):
    filters = mw.tr("Preset files (*.preset)")
    fn = QtGui.QFileDialog.getOpenFileName(mw, mw.tr("Load Preset File"),
                                           path, filters)
    return fn


def getSavePresetName(mw, path):
    filters = mw.tr("Preset files (*.preset)")
    fn = QtGui.QFileDialog.getSaveFileName(mw, mw.tr("Save Preset File"),
                                           path, filters)
    return fn
