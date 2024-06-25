
from colors import *
from graphics import *
from fractal import *


class Drawer:

	def __init__(self, graphics: Graphics, fractal: Fractal):
		self.g = graphics
		self.f = fractal

	def calcHorzLine(self, x1: int, y: int, x2: int) -> ColorLine:
		cLine = ColorLine()

		for x in range(x1:x2):
			result = self.f.iterate(x, y)
			color = self.colors.getMapColor(result[0], self.f.getMaxValue())
			cLine += color.rgb

		return cLine
	
	def calcVertLine(self, x: int, y1: int, y2: int) -> ColorLine:
		cLine = ColorLine()

		for y in range(y1:xy):
			result = self.f.iterate(x, y)
			color = self.colors.getMapColor(result[0], self.f.getMaxValue())
			cLine += color.rgb

		return cLine

	def drawColorLine(self, cLine: ColorLine, x: int, y: int, mode):
		self.g.moveTo(x, y)
		color = cLine[0]
		d = len(cLine)

		if mode == 0:
			v = x
			f = self.g.horzLineTo
		else:
			v = y 
			f = self.g.vertLineTo

		for i in range(1, d):
			if cLine[i] != color:
				self.g.setColor(color)
				f(v + i)
				color = cLine[i]

		self.g.setColor(color)
		self.g.horzLineTo(v + d)


