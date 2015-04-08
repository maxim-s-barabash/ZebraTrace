# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

tr = lambda a: a


def about(mw):
        about = tr("""<center><b>%s</b> version %s.<br><br>
See <a href="http://maxim-s-barabash.github.io/ZebraTrace/">ZebraTrace</a>
for more information.<br><br>
Copyright (C) 2012-2015</center>""")
        about = str(about) % (mw.app.app_name, mw.app.app_version)
        QtGui.QMessageBox.about(mw, tr("About"), about)


def getBitmapFileName(mw, path):
    f = _fromUtf8("*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tga")
    filters = tr("Bitmap files (%s);;All files (*.*)") % f
    fn = QtGui.QFileDialog.getOpenFileName(mw, tr("Open Bitmap File"),
                                           path, filters)
    return fn


def getSaveFileName(mw, path):
    filters = [tr("SVG files (*.svg)"),
               tr("EPS files (*.eps)"),
               tr("NGC g-code files (*.ngc)")
               ]
    filters = ';;'.join(filters)
    fn = QtGui.QFileDialog.getSaveFileName(mw, tr("Save File"),
                                           path, filters)
    return fn


def getPresetName(mw, path):
    filters = tr("Preset files (*.preset)")
    fn = QtGui.QFileDialog.getOpenFileName(mw, tr("Load Preset File"),
                                           path, filters)
    return fn


def getSavePresetName(mw, path):
    filters = tr("Preset files (*.preset)")
    fn = QtGui.QFileDialog.getSaveFileName(mw, tr("Save Preset File"),
                                           path, filters)
    return fn
