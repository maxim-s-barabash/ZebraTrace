# -*- coding: utf-8 -*-
import random
import sys

tr = lambda a: a
from .format_eps import EPS
from .format_gcode import GCode
from .format_svg import SVG


PX = 0
MM = 1
CM = 2
IN = 3

UNITS = ['px', 'mm', 'cm', 'in', '']

BACKENDS = {'.SVG': SVG,
            '.NGC': GCode,
            '.EPS': EPS,
            }

if sys.version_info < (3,):
    xrange = xrange
    reload(sys)
    sys.setdefaultencoding("UTF-8")
    unicode = unicode
else:
    unicode = str
    xrange = range


def id_generator(size=8, chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
    return "".join(random.choice(chars) for _ in range(size))


def unitToPx(v, unit, dpi=90.0):
    value = [round(v, 4), v * dpi / 25.4, v * dpi / 25.4 * 10, v * dpi][unit]
    return value


def pxToUnit(v, unit, dpi=90.0):
    value = [round(v, 4), v / dpi * 25.4, v / dpi * 25.4 / 10, v / dpi][unit]
    return value


def unitToUnit(v, unitBefore, unitAfter, dpi=90.0):
    v = unitToPx(v, unitBefore, dpi)
    value = pxToUnit(v, unitAfter, dpi)
    return value
