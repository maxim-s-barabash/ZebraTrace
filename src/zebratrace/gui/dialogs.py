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
        QtGui.QMessageBox.about(mw, tr("About"), _fromUtf8(about))


def getExtFromFilter(filters):
    return filters.split('*')[1].split(')')[0]

def getBitmapFileName(mw, path):
    f = "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tga"
    filters = str(tr("Bitmap files (%s);;All files (*.*)")) % f
    return QtGui.QFileDialog.getOpenFileName(mw, tr("Open Bitmap File"),
                                           path, _fromUtf8(filters))



def getSaveFileName(mw, path):
    filters = [str(tr("SVG files (*.svg)")),
               str(tr("EPS files (*.eps)")),
               str(tr("NGC g-code files (*.ngc)"))
               ]
               
    filters = u';;'.join(filters)
    return QtGui.QFileDialog.getSaveFileNameAndFilter(mw, tr("Save File"),
                                           path, _fromUtf8(filters))

def getPresetName(mw, path):
    filters = tr("Preset files (*.preset)")
    return QtGui.QFileDialog.getOpenFileName(mw, tr("Load Preset File"),
                                             path, filters)



def getSavePresetName(mw, path):
    filters = tr("Preset files (*.preset)")
    return QtGui.QFileDialog.getSaveFileNameAndFilter(mw, tr("Save Preset File"),
                                                      path, filters)
