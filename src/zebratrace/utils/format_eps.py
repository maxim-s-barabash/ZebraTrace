#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	Copyright 2013 Maxim.S.Barabash <maxim.s.barabash@gmail.com>
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

tr = lambda a:a

class EPS():

	def __init__(self, dom, filename='plot.eps', feedback=None):
		self.dom = dom
		self.filename = filename
		self.feedback = feedback

	def save(self, filename=None):
		if filename == None:
			filename = self.filename
		dom = self.dom
		style = dom.style
		feedback = self.feedback
		if feedback: 
			feed = feedback(text = tr('Save EPS file.'))

		header = '%!PS-Adobe-3.0 EPSF-3.0\n'
		header += '%%Creator: ZebraTRACE v0.5a\n'
		header += '%%Pages: 1\n'
		header += '%%LanguageLevel: 2\n'
		header += '%%%%BoundingBox: %i %i %i %i\n'  % \
					(dom.x1, dom.y1, dom.w, dom.h)
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
		header += '%%%%PageBoundingBox: %i %i %i %i\n'  % \
					(dom.x1, dom.y1, dom.w, dom.h)
		header += '%%EndPageSetup\n'
		header += '0 g\n'


		footer = 'Q Q\n'
		footer += 'showpage\n'
		footer += '%%Trailer\n'
		footer += 'end restore\n'
		footer += '%%EOF\n'


		body = ''.join(reversed([self.pathAsEPS(s) for s in dom.data]))

		f = open(filename, 'wb')                # write to file
		f.write(header.encode('utf-8'))
		f.write(body.encode('utf-8'))
		f.write(footer.encode('utf-8'))
		f.close()

		if feedback: feedback()


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


	def pathAsEPS(self, s):
		scale = self.dom.scale / 0.75
		path = ''
		for p in s:
			if len(p) < 2:
				continue
			path += '%g %g m \n' % (p.node[0].x / scale, p.node[0].y / scale * -1)
			path += ''.join(['%g %g l \n' % (n.x / scale, n.y / scale * -1) for n in p.node[1:]])
			path += [' ', 'h\n'][p.close_path]
		path += 'f\n'
		return path

