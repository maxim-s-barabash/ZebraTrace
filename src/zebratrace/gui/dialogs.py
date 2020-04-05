#    Copyright 2018 Maxim.S.Barabash <maxim.s.barabash@gmail.com>
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

from PyQt5.QtWidgets import QFileDialog, QMessageBox

tr = lambda a: a


def about(mw):
        about_tmpl = tr(u"""<center><b>%s</b> version %s.<br><br>
See <a href="http://maxim-s-barabash.github.io/ZebraTrace/">ZebraTrace</a>
for more information.<br><br>
Copyright (C) 2012-2020</center>""")
        about = about_tmpl % (mw.app.app_name, mw.app.app_version)
        QMessageBox.about(mw, tr("About"), about)


def getExtFromFilter(filters):
    return filters.split('*')[1].split(')')[0]


def getBitmapFileName(mw, path):
    f = "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.tga"
    filters = tr("Bitmap files (%s);;All files (*.*)") % f
    return QFileDialog.getOpenFileName(mw, tr("Open Bitmap File"), path, filters)[0]


def getSaveFileName(mw, path):
    filters = [tr("SVG files (*.svg)"),
               tr("EPS files (*.eps)"),
               tr("NGC g-code files (*.ngc)")
               ]
    filters = u';;'.join(filters)
    return QFileDialog.getSaveFileName(mw, tr("Save File"), path, filters)


def getPresetName(mw, path):
    filters = tr("Preset files (*.preset)")
    return QFileDialog.getOpenFileName(mw, tr("Load Preset File"), path, filters)[0]


def getSavePresetName(mw, path):
    filters = tr("Preset files (*.preset)")
    return QFileDialog.getSaveFileName(mw, tr("Save Preset File"), path, filters)
