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

tr = lambda a: a


class SVG():

    def __init__(self, dom, filename='plot.svg', feedback=None):
        self.dom = dom
        self.filename = filename
        self.feedback = feedback

    def save(self, filename=None):
        if filename is None:
            filename = self.filename
        dom = self.dom
        style = dom.style
        feedback = self.feedback
        if feedback:
            feed = feedback(text=tr('Save SVG file.'))

        header = '<?xml version="1.0" encoding="utf-8"?>\n'
        header += '<svg xmlns="http://www.w3.org/2000/svg" '
        header += 'xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="none" \n'
        header += 'strok_width="%i" stroke="%s" fill="%s" \n' % \
                  (style.strok_width, style.stroke, style.fill)
        header += 'width="%i" height="%i" viewBox="%f %f %f %f">\n<g>\n' % \
                  (dom.w, dom.h, dom.x1, dom.y1, dom.dx, dom.dy)

        footer = "</g>\n</svg>"

        body = ''.join(reversed([self.pathAsSVG(s) for s in dom.data]))

        f = open(filename, 'wb')                # write to file
        f.write(header.encode('utf-8'))
        f.write(body.encode('utf-8'))
        f.write(footer.encode('utf-8'))
        f.close()

        if feedback:
            feedback()

    def pathStyle(self, s):
        style = self.dom.style
        path_style = ""

        if s.style.stroke != style.stroke:
            path_style += 'stroke="%s" ' % (s.style.stroke)
        if s.style.strok_width != style.strok_width:
            path_style += 'strok_width="%s" ' % (s.style.strok_width)
        if s.style.fill != style.fill:
            path_style += 'fill="%s" ' % (s.style.fill)

        return path_style

    def pathAsSVG(self, s):
        path = ''
        path += '<path %s d="' % (self.pathStyle(s))
        for p in s:
            if len(p) < 2:
                continue
            path += 'M%g,%g' % (p.node[0].x, p.node[0].y)
            path += ''.join(['L%g,%g' % (n.x, n.y) for n in p.node[1:]])
            path += [' ', 'Z'][p.close_path]
        path += '"/>\n'
        return path
