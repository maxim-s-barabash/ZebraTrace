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

from PyQt5.QtGui import QImage, QColor, qGray
from .. import event


tr = lambda a: a
GRAYSCALE_COLORTABLE = [QColor(i, i, i).rgb() for i in range(256)]


def grayscale(image):
    return image.convertToFormat(QImage.Format_Indexed8, GRAYSCALE_COLORTABLE)


def desaturate(image):
    p = 100.0 / image.height()
    msg = tr('Desaturate the Image. Press ESC to Cancel.')
    pixel = image.pixel

    event.CANCEL = False
    if not image.isGrayscale():
        tem_image = QImage(image.width(), image.height(), QImage.Format_Indexed8)
        tem_image.setColorTable(GRAYSCALE_COLORTABLE)
        width = range(image.width())
        for imy in range(image.height()):
            for imx in width:
                lightness = qGray(pixel(imx, imy))
                tem_image.setPixel(imx, imy, lightness)
            event.emit(event.APP_STATUS, text=msg, progress=p * imy)
            if event.CANCEL:
                break
        if not event.CANCEL:
            image = tem_image

    event.emit(event.APP_STATUS)

    return image
