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

import random
import sys

from .format_eps import EPS
from .format_gcode import GCode
from .format_svg import SVG


tr = lambda a: a
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
