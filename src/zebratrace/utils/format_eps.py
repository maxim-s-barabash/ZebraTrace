#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright 2015 Maxim.S.Barabash <maxim.s.barabash@gmail.com>
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
from .. import __version__
from .. import event
import textwrap


class EPS():

    def __init__(self, dom, filename='plot.eps'):
        self.dom = dom
        self.filename = filename

    def save(self, filename=None, dpi=90.0):
        from . import tr
        if filename is None:
            filename = self.filename
        dom = self.dom
        scale = dom.scale / 0.75 * dpi / 90.0
        shift = (dom.x1, dom.y1 + dom.dy)

#        style = dom.style
        event.emit(event.APP_STATUS, text=tr('Save EPS file.'))

        header = '%!PS-Adobe-3.0 EPSF-3.0\n'
        header += '%%Creator: ZebraTRACE v%s\n' % __version__
        header += '%%Pages: 1\n'
        header += '%%LanguageLevel: 2\n'
        header += '%%%%BoundingBox: %i %i %i %i\n' % \
                  (0, 0, dom.w / dpi * 72., dom.h / dpi * 72.)
        header += '%%EndComments\n'
        header += '%%BeginProlog\n'
        header += 'save\n'
        header += '50 dict begin\n'
        header += '/q { gsave } bind def\n'
        header += '/Q { grestore } bind def\n'
        header += '/m { moveto } bind def\n'
        header += '/l { lineto } bind def\n'
        header += '/h { closepath } bind def\n'
        header += '/f { fill } bind def\n'
        header += '/f* { eofill } bind def\n'
        header += '/n { newpath } bind def\n'
        header += '/g { setgray } bind def\n'
        header += '%%EndProlog\n'
        header += '%%Page: 1 1\n'
        header += '%%BeginPageSetup\n'
        header += '%%%%PageBoundingBox: %i %i %i %i\n' % \
                  (0, 0, dom.w / dpi * 72., dom.h / dpi * 72.)
        header += '%%EndPageSetup\n'
        header += '0 g\n'

        footer = 'Q Q\n'
        footer += 'showpage\n'
        footer += '%%Trailer\n'
        footer += 'end restore\n'
        footer += '%%EOF\n'

        body = ''.join(reversed([self.pathAsEPS(s, scale, shift) for s in dom.flat_data]))

        f = open(filename, 'wb')                # write to file
        f.write(header.encode('utf-8'))
        f.write(body.encode('utf-8'))
        f.write(footer.encode('utf-8'))
        f.close()

        event.emit(event.APP_STATUS)

    def pathAsEPS(self, s, scale, shift):
        shift_x, shift_y = shift

        px = lambda x: (x - shift_x) / scale
        py = lambda y: (y - shift_y) / scale * -1.0

        path = ''
        for p in s:
            if len(p) < 2:
                continue
            path += ''.join([('%g %g l ' if i else '%g %g m ') % (px(n.x), py(n.y)) for i, n in enumerate(p.node)])
            path += 'h ' if p.close_path else ' '
        path += 'f'
        path = textwrap.fill(path, 250) + '\n'

        return path
