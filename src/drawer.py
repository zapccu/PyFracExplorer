
from colors import *
from graphics import *
from fractal import *


class Drawer:

	def __init__(self, graphics: Graphics, fractal: Fractal):
		self.graphics = graphics
		self.fractal = fractal

	# Iterate a line from x, y
	# orientation: 0 = horizontal, 1 = vertical
	def calculateLine(self, x: int, y: int, xy: int, orientation: int) -> ColorLine:
		cLine = ColorLine()

		if orientation == 0:
			r = range(x, xy)
		else:
			r = range(y, xy)

		for v in r:
			if orientation == 0:
				result = self.fractal.iterate(v, y)
			else:
				result = self.fractal.iterate(x, v)
			color = self.graphics.colors.getMapColor(result[0], self.fractal.getMaxValue())
			cLine += color.rgb

		return cLine
	
	# Draw a color line from (x, y)
	# orientaion: 0 = horizontal, 1 = vertical
	def drawColorLine(self, cLine: ColorLine, x: int, y: int, orientation: int):
		self.g.moveTo(x, y)
		color = cLine[0]
		d = len(cLine)

		if orientation == 0:
			v = x
			lineTo = self.graphics.horzLineTo
		else:
			v = y 
			lineTo = self.graphics.vertLineTo

		for i in range(1, d):
			if cLine[i] != color:
				self.graphics.setColor(color)
				lineTo(v + i)
				color = cLine[i]

		self.graphics.setColor(color)
		lineTo(v + d)


