
from tkinter import *
from fractal import *
from colors import *
from gui import *


class Graphics:

	# Drawing canvas
	canvas = None

	# Canvas dimensions
	width = 0
	height = 0

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
		self.canvas    = drawFrame.canvas
		self.width     = drawFrame.canvasWidth
		self.height    = drawFrame.canvasHeight
		self.flipY     = flipY
		self.setColor(0)

	def beginDraw(self, width: int, height: int) -> bool:
		self.drawFrame.setCanvasRes(width, height)
		self.width = width
		self.height = height
		return True

	def endDraw(self):
		return
	
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

	""""

	def drawPalette(self):
		for i in range(len(self.colors)):
			self.setColor(i)
			self.moveTo(10, 10+i)
			self.horzLineTo(200)

	def drawLineByLine(self, fractal: Fractal, width: int, height: int) -> bool:
		if self.beginDraw(fractal, width, height) == False:
			return False

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
		
		calcTime = self.endDraw(fractal)
		print(f"{calcTime} seconds")

		return True

	def drawSquareEstimation (self, x1: int, y1: int, x2: int, y2: int,
							colTop: ColorLine, colBottom: ColorLine, colLeft: ColorLine, colRight: ColorLine):

		minLen = min(x2-x1, y2-y1)

		if minLen < 2:
			# Nothing more to draw
			return

		elif colTop.isUnique() and colTop == colBottom and colLeft == colRight and colLeft == colTop:
			# Fill rectangle
			self.setColor(colTop.getColor())
			self.fillRect(x1, y1, x2, y2)

		elif minLen < self.minLen:
			# Draw line by line
			return self.drawLineByLine (x1+1, y1+1, x2-1, y2-1)

		else:
			# Split into child squares
			xMid = x1+(x2-y1)/2
			yMid = y1+(y2-y1)/2

			# Calculate outlines of resulting squares
			rleTopLeft     = self.calculateHorzLine(x1, y1, xMid, y1)
			rleTopRight    = self.calculateHorzLine(xMid, y1, x2, y1)
			rleBottomLeft  = self.calculateHorzLine(x1, y2, xMid, y2)
			rleBottomRight = self.calculateHorzLine(xMid, y2, x2, y2)
			rleLeftTop     = self.calculateVertLine(x1, y1, x1, yMid)
			rleLeftBottom  = self.calculateVertLine(x1, yMid, x1, y2)
			rleRightTop    = self.calculateVertLine(x2, y1, x2, yMid)
			rleRightBottom = self.calculateVertLine(x2, yMid, x2, y2)

			# Recursively call 
			return self.drawSquareEstimation()

	def splitSquare(self, x1, y1, x2, y2):
		xm = x1+(x2-x1)/2
		ym = y1+(y2-y1)/2

	"""