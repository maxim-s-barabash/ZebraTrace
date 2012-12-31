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
import os


path_zebra = os.path.dirname(__file__)
path_gui = os.path.join(path_zebra, 'gui')
#path_widgets = os.path.join(path_gui, 'widgets')
#path_geom = os.path.join(path_zebra, 'geom')
#path_utils = os.path.join(path_zebra, 'utils')

#sys.path.append(path_zebra)
sys.path.append(path_gui)
#sys.path.append(path_widgets)
#sys.path.append(path_geom)
#sys.path.append(path_utils)


from PyQt4.QtGui import *
from PyQt4.QtCore import *
from .app_config import *
from .app import *



##############################################

def zebratrace():
	app_data = AppData()
	config = AppConfig()
	app = QApplication(sys.argv)
	try:
		lang = app_data.lang
		translate_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
		transl = QTranslator(app)
		if not(transl.load('zebratrace_' + lang, translate_path)):
			transl.load('zebratrace_' + lang, app_data.translations_dir)
		app.installTranslator(transl)
	except locale.Error:
		pass

	window = MainWindow(app_data, config)
	if len(sys.argv) == 2:
		window.openFileBitmap(sys.argv[1])
	window.show()

	sys.exit(app.exec_())
