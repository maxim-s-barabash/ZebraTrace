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


import os
import tempfile
import utils

from utils.jsonconfig import *

default_preset = {
  "funcX": "(0.95+0.02*sin(20*a))*i/n", 
  "funcY": "", 
  "rangeMax": 6.28318530718,
  "rangeMin": 0.0
}

default_config = {
  "currentPath": "",
  "presetPath": "./preset/",
  "trace_image": "",
  "numberCurves": 80,
  "curveResolution": 0.3,
  "curveWidthMin": 1,
  "curveWidthMax": 5,
  "nodeReduction": 0,
}

TEMP_PREFIX = "TRACE_"


class AppData:
	app_name = "ZebraTRACE"
	app_version = "0.3 alpha"
	app_config_dir = os.path.join("~", ".config", "zebratrace")
	app_config_dir = unicode(os.path.expanduser(app_config_dir))
	if not os.path.lexists(app_config_dir):
		os.makedirs(app_config_dir)
	app_config = unicode(os.path.join(app_config_dir, "preferences.cfg"))
	temp_dir = tempfile.gettempdir()
	temp_svg = unicode(os.path.join(temp_dir, TEMP_PREFIX + 
							utils.id_generator() + ".svg"))


class Preset(JsonConfigParser):
	def __init__(self):
		self.update(default_preset)


class AppConfig(JsonConfigParser):
	def __init__(self):
		self.update(default_config)


if __name__ == "__main__":
	"""TEST"""
	app_data = AppData()
	print utils.id_generator()

