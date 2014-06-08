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


import sys, os
import PyQt4

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
	base = "Win32GUI"
plug_dir = os.path.join(os.path.dirname(PyQt4.__file__),
				"plugins", 'imageformats')


buildOptions = dict(
		create_shared_zip = True,
		compressed = True,
		include_files = ["src/translations", "src/preset", (plug_dir, "imageformats")],
		base = base,
		include_msvcr = True,
		)
		
msiOptions = dict(
		upgrade_code = True,
		add_to_path = False, 
		)

setup(
	name = "ZebraTRACE",
	version = "0.5",
	author = "Maxim Barabash",
	author_email = "maxim.s.barabash@gmail.com",
	description = "ZebraTrace is a simple tool to trace bitmap images into a pattern of curves with a variable width",
	options = dict(build_exe = buildOptions, bdist_msi = msiOptions),
	executables = [Executable("ZebraTrace.pyw", 
					base = base, 
					icon = "images/zebra.ico",
					copyDependentFiles=True,
					shortcutDir = "ProgramMenuFolder",
					shortcutName = "ZebraTrace")
					])

