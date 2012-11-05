#!/usr/bin/env python
# -*- coding: cp1251 -*-

# =============================================================
# FunctionPlotter

# Модуль для рисования графиков функций
# Python 2.6, Qt4 4.6

# Содержимое этого файла — общественное достояние.

# The contents of this file are dedicated to the public domain.
# =============================================================


import sys, os
from math import *
# для трассировки изображения используется PyQt4 (http://www.riverbankcomputing.co.uk/software/pyqt/download)

sys.setcheckinterval(0xfff)

class FuncPlotter:
    def __init__(self, wh, rect, grid_lines=0, trace_image='', width_range=[0.1, 2]):
        """ Рисует графики функций. 
        
        Параметры:
        wh              — список [ширина, высота], задающий размер изображения SVG в пикселах
        rect            — список [x1, y1, x2, y2] — границы координатной плоскости
        grid_lines      — целое число, задающее количество линий сетки, 0 — отсутствие сетки
        trace_image     — строка, задающая имя файла изображения для трассировки
        width_range     — список из двух значений, определяющий диапазон толщин линии при трассировке
        """
        self.x1 = float(rect[0]); self.y1 = float(rect[1])
        self.x2 = float(rect[2]); self.y2 = float(rect[3])
        self.dx = float(self.x2 - self.x1)
        self.dy = float(self.y2 - self.y1)
        
        self.w = float(wh[0])
        self.h = float(wh[1])
        
        self.scale = float(self.dx)/self.w      # разрешение поля в единицах SVG на пиксел
        self.grid = grid_lines
        self.data = []
        
        self.img = None
        self.trace_image = trace_image
        if trace_image and os.path.exists(trace_image):
            from PyQt4.QtGui import QImage  
            self.img = QImage(trace_image)      # изображение для трассировки должно состоять из 256 индексных цветов, 
                                                # ранжированных по количеству белого (grayscale)
            self.img = self.img.convertToFormat(QImage.Format_Indexed8)
            self.width_range = width_range
            self.img_w = self.img.width()
            self.img_h = self.img.height()
            self.img_colors = float(self.img.colorCount()-1)


    def _generate_path(self, coords=[], color='black', width=1, close_path=False):
        """ Генерирует элемент <path/> с заданными параметрами и координатами.
        
        Координаты передаются в виде [[x1,y1], [x2,y2], [x3,y3], ...].
        """
        if not coords:
            coords = self.coords
            
        path = '\n\t\t<path stroke="%s" stroke-width="%s" d="M%f,%f ' % (color, width*self.scale, coords[0][0], coords[0][1])
        path += ''.join(['L%f,%f ' % (x, y) for x,y in coords[1:]]) + ['"/>', 'Z"/>'][close_path]
        
        self.data.append(path)


    def _trace_image(self):
        """ Изменяет координаты (coords) кривой в зависимости от цвета изображения. 
        
        Здесь мы берём две соседние точки и вычисляем угол (alpha), под которым идёт линия,
        перпендикулярная к касательной к кривой. При помощи этого угла мы проводим
        две соединяющиеся на концах параллельные кривые (right и left) взамен старой (coords),
        отстоящие друг от друга на расстоянии, зависящем от индекса цвета изображения.
        """
        coords = self.coords
        
        delta = (self.width_range[1]-self.width_range[0])/2.0
        min_width = self.width_range[0]/2.0
        
        right = coords[:]
        left  = coords[:]
        
        canvas_x1 = self.x1                             # OPTIMIZATION
        canvas_y1 = self.y1
        canvas_dx = self.dx
        canvas_dy = self.dy
        img_w = self.img_w
        img_h = self.img_h
        img_colors = self.img_colors
        img_pixelIndex = self.img.pixelIndex
        scale = self.scale
        
        pre_x, pre_y = coords[-1]
        for i,[x,y] in enumerate(coords):        
            if pre_y<y:
                alpha = atan((pre_x-x)/(y-pre_y))
            elif pre_y==y:
                alpha = pi/2
            else:
                alpha = atan((pre_x-x)/(y-pre_y)) + pi

            pixel_x = int((x-canvas_x1)/canvas_dx*img_w)
            pixel_y = int((y-canvas_y1)/canvas_dy*img_h)
            
            if pixel_x>=0 and pixel_x<img_w and pixel_y>=0 and pixel_y<img_h:
                k = 1-img_pixelIndex(pixel_x, pixel_y)/img_colors
            else:
                k = 0
    
            d = (min_width + k*delta)*scale
            
            dx = d*cos(alpha)
            dy = d*sin(alpha)
            
            right[i] = [x+dx, y+dy]
            left[i]  = [x-dx, y-dy]
            
            pre_x, pre_y = x, y
            
        left.reverse()
        self.coords = right+left+[right[0]]


    def append_func(self, fX, fY, T, res=1, color='black', width=3, close_path=True):
        """ Добавляет график функций fX(t) и fY(t).
        
        fX          — функция одной переменной, вычисляющая координату x или функция радиуса от угла, если следующий параметр (fY) возвращает False
        fY          — функция одной переменной, вычисляющая координату y или None
        T           — список из двух значений, определяющий диапазон переменной
        color       — строка, задающая цвет обводки кривой, можно использовать именованные значения из спецификации SVG или 'none'
        width       — толщина контура
        close_path  — параметр, указывающий на то, нужно ли замыкать кривую или нет
        """
        dT = float(T[1] - T[0])
        resolution = int(dT/self.scale*res)
        coords = []
        
        if not fY:                              # если задана только функция x
            fR = fX                             # то считать координаты полярными
            fX = lambda a: fR(a)*cos(a)
            fY = lambda a: fR(a)*sin(a)
        
        tl = [T[0]+dT/resolution*i for i in xrange(resolution+1)]
        coords = zip(map(fX,tl), map(fY,tl))    # координата y перевёрнута (отрицательные значения вверху)
            
        self.coords = coords
        
        if self.img:                            # если есть картинка, то трассируем
            self._trace_image()                 # (результат записывается в self.coords)
            
        self._generate_path([], color, width, close_path)
        

    def plot(self, file_name='plot.svg'):
        """ Сохраняет сгенерированные <path/> в файл SVG. 
        """
        if self.grid:                           # если нужна сетка, то рисуем её с толщиной по-умолчанию и более тёмной линией в центре
            g = self.grid
            for i in xrange(g+1):
                self._generate_path([[self.x1+self.dx/g*i, self.y1], [self.x1+self.dx/g*i, self.y2]], ['grey', 'lightgrey'][bool(i-g/2)])
                self._generate_path([[self.x1, self.y1+self.dy/g*i], [self.x2, self.y1+self.dy/g*i]], ['grey', 'lightgrey'][bool(i-g/2)])

        header  = """<?xml version="1.0" encoding="utf-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="none" """
        header += """width="%i" height="%i" viewBox="%f %f %f %f">\n\t<g fill="%s">\n""" % \
                  (self.w, self.h, self.x1, self.y1, self.dx, self.dy, ['none', 'black'][bool(self.img)])
        imag = '  <image y="-1" x="-1" xlink:href="%s" height="2" width="2" opacity=".2" />' % (self.trace_image)
        footer  = "\n\n\t</g>\n\n</svg>"

        f = open(file_name, 'w')                # записываем в файл
        f.write(header)
        f.write(imag)
        f.write(''.join(reversed(self.data)))
        f.write(footer)
        f.close()


# пример использования:
if __name__ == '__main__':
    
    image_size = [500, 500]
    dimensions = [-1, -1, 1, 1]
    
    fp = FuncPlotter(image_size, dimensions, grid_lines=20)
    
    curve_resolution = 0.05
    width = 2
    
    # график в прямоугольных координатах
    x = lambda t: t
    y = lambda t: 0.5*sin(t*pi)
    fp.append_func(x, y, [-1, 1], curve_resolution, 'green', width)
    
    # график в полярных координатах при равнопеременном угле
    r = lambda a: sin(a*2)
    fp.append_func(r, None, [0, 2*pi], curve_resolution, 'red', width)

    fp.plot()

