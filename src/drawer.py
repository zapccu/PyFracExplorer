
from colors import *
from graphics import *
from fractal import *


class Drawer:

	HORIZONTAL = 0
	VERTICAL = 1

	# Flag: True = drawing in progress
	bDrawing = False

	def __init__(self, graphics: Graphics, fractal: Fractal):
		self.graphics = graphics
		self.fractal = fractal

	# Iterate a line from x, y
	# orientation: 0 = horizontal, 1 = vertical
	def calculateLine(self, x: int, y: int, xy: int, orientation: int) -> ColorLine:
		cLine = ColorLine()
		r = range(x, xy) if orientation == 0 else range(y, xy)

		for v in r:
			result = self.fractal.iterate(v, y) if orientation == 0 else self.fractal.iterate(x, v)
			color = self.graphics.colors.getMapColor(result[0], self.fractal.getMaxValue())
			cLine += color.rgb

		return cLine
	
	# Draw a color line from (x, y)
	# orientaion: 0 = horizontal, 1 = vertical
	def drawColorLine(self, cLine: ColorLine, x: int, y: int, orientation: int):
		self.graphics.moveTo(x, y)
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

	def beginDraw(self, width: int, height: int) -> bool:
		if self.bDrawing == False:
			if self.graphics.beginDraw(width, height) == False: return False
			if self.fractal.beginCalc(width, height) == False: return False
			self.bDrawing = True
		return self.bDrawing
	
	def endDraw(self) -> float:
		if self.bDrawing == True:
			calcTime = self.fractal.endCalc()
			self.graphics.endDraw()
			self.bDrawing = False
			return calcTime
		else:
			return 0.0

	def drawLineByLine(self, x: int, y: int, width: int, height: int) -> bool:
		if self.beginDraw(width, height) == False:
			return False

		print("Line by Line")
		for y in range(height):
			print(f"Calculating line {y}")
			cLine = self.calculateLine(x, y, x+width, Drawer.HORIZONTAL)
			self.drawColorLine(cLine, x, y, Drawer.HORIZONTAL)
		
		calcTime = self.endDraw()
		print(f"{calcTime} seconds")

		return True