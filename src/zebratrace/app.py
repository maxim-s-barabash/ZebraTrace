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


from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QLibraryInfo, QTranslator

from app_config import locale, AppData, AppConfig
from app_mw import MainWindow


class ZQApplication(AppData, QApplication):
    def __init__(self, argv):
        super(ZQApplication, self).__init__(argv)
        self.config = AppConfig()
        self.locale()
        self.mw = MainWindow(self)

    def locale(self, lang=None):
        try:
            lang = lang or self.lang
            translate_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
            transl = QTranslator(self)
            fn = 'zebratrace_%s' % lang
            if not(transl.load(fn, translate_path)):
                transl.load(fn, self.translations_dir)
            self.installTranslator(transl)
        except locale.Error:
            pass

    def run(self, argv):
        self.mw.show()
        if len(argv) == 2:
            self.mw.openFileBitmap(argv[1])
