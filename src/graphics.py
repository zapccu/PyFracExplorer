
from tkinter import *
from fractal import *
from colors import *
from gui import *


class Graphics:

	# Drawing canvas
	canvas = None

	# Flip vertical orientation
	flipY = False

	# Color palette. Default palette contains 1 color (white). Default color is black
	colors = ColorTable()

	# Current color
	color = '#ffffff'

	# Current drawing position
	x = 0
	y = 0

	# Flip vertical coordinates
	def flip(self, y: int) -> int:
		if self.flipY:
			return self.height-y-1
		else:
			return y

	def __init__(self, drawFrame: DrawFrame, flipY = False):
		self.drawFrame = drawFrame
		self.canvas = drawFrame.canvas
		self.width = drawFrame.canvasWidth
		self.height = drawFrame.canvasHeight
		self.flipY = flipY
		self.setColor(0)

	# Set drawing position
	def moveTo(self, x: int, y: int):
		self.x = x
		self.y = y

	# Set color palette
	def setColorTable(self, colorTable: ColorTable):
		self.colors = colorTable

	# Set color to palette entry or specified color
	def setColor(self, color):
		if type(color) == int:
			self.colorIdx = color
			self.color = self.colors.getColor(color).rgbStr()
		elif type(color) == Color:
			self.color = color.rgbStr()
		elif type(color) == str:
			self.color = color

	# Draw a horizontal line excluding end point
	# Set drawing position to end point
	def horzLineTo(self, x: int):
		if x >= 0 and x != self.x:
			self.canvas.create_line(self.x, self.flip(self.y), x, self.flip(self.y), fill=self.color, width=1)
			self.x = x

	# Draw vertical line excluding end point
	# Set drawing position to end point
	def vertLineTo(self, y: int):
		if y >= 0 and y != self.y:
			self.canvas.create_line(self.x, self.flip(self.y), self.x, self.flip(y), fill=self.color, width=1)
			self.y = y

	def lineTo(self, x: int, y: int):
		if x >= 0 and y >= 0 and (x != self.x or y != self.y):
			self.canvas.create_line(self.x, self.flip(self.y), x, self.flip(y), fill=self.color, width=1)
			self.x = x
			self.y = y

	# Draw a filled rectangle
	# Drawing position is not updated
	def fillRect(self, x1: int, y1: int, x2: int, y2: int):
		self.canvas.create_rectangle(x1, self.flip(y1), x2, self.flip(y2), fill=self.color, outline=self.color)

	def drawPalette(self):
		for i in range(self.colors.maxColors()):
			self.setColor(i)
			self.moveTo(10, 10+i)
			self.horzLineTo(200)

	def calculateHorzLine(self, fractal: Fractal, x1: int, x2: int, y: int):
		cLine = ColorLine(fractal.iterate(x1, y))
		for x in range(x1+1, x2+1):
			cLine += fractal.iterate(x, y)
		return cLine

	def calculateVertLine(self, fractal: Fractal, x: int, y1: int, y2: int):
		cLine = ColorLine(fractal.iterate(x, y1))
		for y in range(y1+1, y2+1):
			cLine += fractal.iterate(x, y)
		return cLine
	
	def drawColorLine(self, x: int, y: int, direction: int, cLine: ColorLine):
		self.moveTo(x, y)

		for i in range(len(cLine)):
			length, color = cLine[i]
			self.setColor(color)
			if direction == 0:
				self.horzLineTo(self.x+length)
			else:
				self.vertLineTo(self.y+length)

	def drawColorRectangle(self, x1: int, y1: int, x2: int, y2: int, cLines):
		for cLine in ((x1, y1, 0, cLines[0]), (x1, y2, 0, cLines[1]), (x1, y1, 1, cLines[2]), (x2, y1, 1, cLines[3])):
			self.drawColorLine(cLine[0], cLine[1], cLine[2], cLine[3])
	
	def drawLineByLine(self, fractal: Fractal):
		fractal.beginCalc()
		for y in range(self.height):
			self.drawFrame.parentWindow.update_idletasks()

			self.moveTo(0, y)
			r = fractal.iterate(0, y)
			color = self.colors.getMapColor(r[0], fractal.getMaxValue())
			self.setColor(color)

			for x in range(1, self.width):
				r = fractal.iterate(x, y)
				newColor = self.colors.getMapColor(r[0], fractal.getMaxValue())
				if newColor != color:
					self.setColor(color)
					self.horzLineTo(x)
					color = newColor

			self.setColor(color)
			self.horzLineTo(self.width)
		
		calcTime = fractal.endCalc()
		print(f"{calcTime} seconds")

