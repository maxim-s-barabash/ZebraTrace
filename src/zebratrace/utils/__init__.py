# -*- coding: utf-8 -*-
import sys
import random


if sys.version_info < (3,):
	xrange = xrange
	reload(sys)
	sys.setdefaultencoding("UTF-8")
	unicode = unicode
else:
	unicode = str
	xrange = range


def id_generator(size=8, chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
	return "".join(random.choice(chars) for x in range(size))
