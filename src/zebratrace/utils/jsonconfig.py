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
import sys
import json
from . import unicode


def _encode(data):
	if isinstance(data, unicode):
		data = data.encode('utf-8')
	if isinstance(data, bytes):
		data = data.decode('utf-8')
	elif isinstance(data, list):
		data = _encode_list(data)
	elif isinstance(data, dict):
		data = _encode_dict(data)
	return data


def _encode_list(data):
		rv = []
		for item in data:
			rv.append(_encode(item))
		return rv


def _encode_dict(data):
		rv = {}
		#for key, value in data.iteritems():
		for key, value in data.items():
			if isinstance(key, unicode):
				key = key.encode('utf-8').decode('utf-8')
			rv[key] = _encode(value)
		return rv


class JsonConfigParser:

	def update(self, cnf={}):
		if cnf:
			self.__dict__.update(cnf)

	def load(self, filename=None):
		if os.path.exists(filename):
			#try:
				with open(filename, mode='r') as f:
					dic = f.read()
				dic = json.loads(dic, object_hook=_encode_dict)
				self.update(dic)
			#except:
			#	pass

	def save(self, filename=None):
		#if len(self.__dict__) == 0 or filename == None:
		#	return
		#try:
			s = json.dumps(self.__dict__, ensure_ascii=False, indent=2)
			with open(filename, mode='w') as f:
				f.write(s)
		#except (IOError, os.error) as value:
			#sys.stderr('cannot write preferences into %s: %s' % (filename,
			#				value[1]))
			#return
