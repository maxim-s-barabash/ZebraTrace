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


from math import cos, sin
import os
import time

from PyQt4.QtCore import QLibraryInfo, QTranslator, QTimer
from PyQt4.QtGui import QApplication, QMessageBox, QImage

from . import event
from .app_config import Preset, default_preset
from .app_config import locale, AppData, AppConfig
from .app_mw import MainWindow
from .geom.DOM import DOM
from .geom.funcplotter2 import FuncPlotter
from .geom.function import Function
from .geom.image import desaterate, grayscale
from .gui import dialogs
from .utils import BACKENDS
from .utils import unicode, xrange
from . import utils
from .geom import image


# Douglas-Peucker line simplification.
# from .geom.dp import simplify_points
# Visvalingam line simplification.
from .geom.visvalingam import simplify_visvalingam_whyatt as simplify_points


class ZQApplication(AppData, QApplication):
    def __init__(self, argv):
        super(ZQApplication, self).__init__(argv)
        self.document = None
        self.autoTraceTimer = QTimer()
        self.autoTraceTimer.timeout.connect(self.autoTrace)
        self.config = AppConfig()
        lang = getattr(self.config, 'lang', None)
        self.locale(lang)
        self.mw = MainWindow(self)
        self.loadConfig()

    def autoTrace(self):
        self.autoTraceTimer.stop()
        if self.mw.buttonAutoTrace.isChecked():
            self.mw.buttonTrace.clicked.emit(True)

    def locale(self, lang=None):
        try:
            lang = lang or self.lang
            translate_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
            transl = self.transl = QTranslator(self)
            fn = 'zebratrace_%s' % lang
            if not(transl.load(fn, translate_path)):
                transl.load(fn, self.translations_dir)
            self.installTranslator(transl)
            self.tr = lambda a: QApplication.translate("ZQApplication", a)
            dialogs.tr = lambda a: QApplication.translate("@default", a)
            utils.tr = lambda a: QApplication.translate("@default", a)
            image.tr = lambda a: QApplication.translate("@default", a)

        except locale.Error:
            pass

    def run(self, argv):
        self.mw.show()
        if len(argv) == 2:
            self.open(argv[1])

    def quit(self):
        self.saveConfig()
        if os.path.isfile(self.temp_svg):
            os.remove(self.temp_svg)
        return QApplication.quit()

    def loadConfig(self, fn=None):
        if fn is None:
            fn = self.app_config_fn
        self.config.load(fn)

    def saveConfig(self, fn=None):
        if fn is None:
            fn = self.app_config_fn
        self.config.save(fn)

    def open(self, fn=None):
        if not fn:
            fn = dialogs.getBitmapFileName(self.mw, unicode(self.config.currentPath))

        if fn:
            self.mw.view.clean()
            image_fn = unicode(fn)
            self.config.currentPath = unicode(os.path.dirname(image_fn))
            img = QImage(image_fn)
            img_w = float(img.width())
            img_h = float(img.height())
            if img_w:
                self.document = DOM([img_w, img_h])
                self.document.image_fn = image_fn
                img = desaterate(img)
                self.document.image = grayscale(img)
                event.emit(event.DOC_OPENED)
                event.emit(event.DOC_EXPECTS)
            else:
                QMessageBox.warning(self.mw, self.tr("Open file"),
                                    self.tr("This file is corrupt or not supported?"))

    def saveAs(self, fn=None):
        if not fn:
            fn, f = dialogs.getSaveFileName(self.mw, unicode(self.config.currentPath))
            if not fn:
                return
            fn = unicode(fn)
            if not os.path.splitext(fn)[1]:
                fn += dialogs.getExtFromFilter(f)

        if fn:
            fn = unicode(fn)  
            _, ext = os.path.splitext(fn)
            ext = ext.upper()
            self.config.currentPath = unicode(os.path.dirname(fn))
            backend = BACKENDS.get(ext)
            if backend:
                dpi = self.config.dpi
                backend(self.document).save(fn, dpi=dpi)
                event.emit(event.DOC_SAVED)

    def help(self):
        import webbrowser
        url = self.help_index
        webbrowser.open(url)

    def loadPreset(self, fn=None):
        if not fn:
            path = self.config.presetPath or self.preset_dir
            fn = dialogs.getPresetName(self.mw, unicode(path))
        if fn:
            fn = unicode(fn)
            self.config.update(default_preset)
            self.config.load(fn)

    def savePreset(self, fn=None):
        config = self.config
        if not fn:
            fn, f = dialogs.getSavePresetName(self.mw, config.presetPath)
            if not fn:
                return
            fn = unicode(fn)
            if not os.path.splitext(fn)[1]:
                fn += dialogs.getExtFromFilter(f)

        if fn:
            fn = unicode(fn)
            config.presetPath = unicode(os.path.dirname(fn))
            preset = Preset()
            preset.funcX = config.funcX
            preset.funcY = config.funcY
            preset.rangeMin = config.rangeMin
            preset.rangeMax = config.rangeMax
            preset.polar = config.polar
            preset.resolution = config.resolution
            preset.save(fn)

    def about(self):
        dialogs.about(self.mw)

    def docClean(self):
        self.autoTraceTimer.start(1500)
        if self.document:
            self.document.clean()

    def docFlatClean(self):
        self.autoTraceTimer.start(700)
        if self.document:
            self.document.flat_data = []

    def getFunctions(self, variables):
        config = self.config
        try:
            funcX = Function(config.funcX)
        except (SyntaxError, TypeError, NameError, ZeroDivisionError) as err:
            QMessageBox.critical(self.mw, self.tr("Error in function"), "%s\n%s" % (config.funcX, unicode(err)))
            return
        try:
            funcY = Function(config.funcY)
        except (SyntaxError, TypeError, NameError, ZeroDivisionError) as err:
            QMessageBox.critical(self.mw, self.tr("Error in function"), "%s\n%s" % (config.funcX, unicode(err)))
            return
        fX = funcX(variables)
        fY = funcY(variables)
        if config.polar and fY:
            fR, fT = fX, fY
            fX = lambda a: fR(a) * cos(fT(a))
            fY = lambda a: fR(a) * sin(fT(a))
        elif not fY:  # If only the function x
            fR = fX  # then consider the polar coordinates
            fX = lambda a: fR(a) * cos(a)
            fY = lambda a: fR(a) * sin(a)
        return fX, fY

    def trace(self):
        document = self.document
        if document is None or not document.image:
            return
        event.emit(event.DOC_TRACE)
        if not document.data:
            self._tarce(document)

        if not document.flat_data:
            self.strokeToPath()
            self.simplify()
        self.savePreview()

        event.emit(event.DOC_MODIFIED)
        event.emit(event.DOC_EXPECTS)

    def _tarce(self, document):
        config = self.config
        alpha = [config.rangeMin, config.rangeMax]  # range of the variable
        resolution = config.resolution  # curve quality
        stroke_color = "none"  # no stroke (when tracing is used fill)

        width_range = [config.curveWidthMin, config.curveWidthMax]
        fp = FuncPlotter(document, width_range=width_range)

        variables = {}
        f = self.getFunctions(variables)
        if f:
            fX, fY = f
            n = config.numberCurves  # number of curves
            variables['n'] = 1.0 * n

            # Step 1. Make Path
            dprogres = 100.0 / n
            msg = self.tr('Trace the Image. Press ESC to Cancel.')
            info = document.info
            info['trace_start'] = time.time()
            event.CANCEL = False
            for i in xrange(1, n + 1):
                event.emit(event.APP_STATUS, text=msg, progress=dprogres * i)
                if not event.CANCEL:
                    try:
                        variables['i'] = i
                        auto_resolution = fp.auto_resolution2(fX, fY, alpha)
                    except (SyntaxError, TypeError, NameError, ZeroDivisionError) as err:
                        QMessageBox.critical(self.mw, self.tr("Error in function"),
                                             unicode(err))
                        break

                    fp.append_func(fX, fY, alpha, resolution * auto_resolution,
                                   stroke_color, close_path=True)
                else:
                    break
            info['trace_end'] = time.time()

    def savePreview(self):
        document = self.document
        previewSVG = BACKENDS['.SVG'](document)
        previewSVG.save(self.temp_svg)

    def strokeToPath(self):
        d = self.document
        writing = self.config.curveWriting
        dprogres = 100.0 / (len(d) or 1)
        msg = self.tr('Flatten paths')
        info = d.info
        info['flatten_paths_start'] = time.time()
        d.flat_data = []
        for i, path in enumerate(d):
            event.emit(event.APP_STATUS, text=msg, progress=dprogres * i)
            p = path.getStrokeAsPath(writing)
            d.flat_data.append(p)
        info['flatten_paths_end'] = time.time()

    def simplify(self):
        d = self.document
        tolerance = self.config.nodeReduction / 100. * d.scale
        if tolerance > 0.0:
            dprogres = 100.0 / (len(d) or 1)
            msg = self.tr('Simplify Points')
            for i, path in enumerate(d.flat_data):
                event.emit(event.APP_STATUS, text=msg, progress=dprogres * i)
                for j in xrange(len(path)):
                    path[j].node = simplify_points(path[j].node, tolerance)
