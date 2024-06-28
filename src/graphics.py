
from tkinter import *
from fractal import *
from colors import *
from gui import *

"""
Class for graphic operations
"""

class Graphics:

	def __init__(self, drawFrame: DrawFrame, flipY = False):
		self.drawFrame = drawFrame
		self.canvas    = drawFrame.canvas
		self.width     = drawFrame.canvasWidth
		self.height    = drawFrame.canvasHeight
		self.flipY     = flipY
		self.colors    = ColorTable()

		self.moveTo(0, 0)
		self.setColor(idx = 0)

	# Flip vertical coordinates
	def flip(self, y: int) -> int:
		if self.flipY:
			return self.height-y-1
		else:
			return y

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
	def setColor(self, idx: int = -1, strColor: str = '', intColor: int = Color.NOCOLOR):
		if idx >= 0:
			self.colorIdx = idx
			self.color = Color.rgbStr(self.colors[idx])
		elif strColor != '':
			self.color = strColor
		elif intColor != Color.NOCOLOR:
			self.color = Color.rgbStr(intColor)

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

	# Draw a filled rectangle excluding right and bottom line
	# Drawing position is not updated
	def fillRect(self, x1: int, y1: int, x2: int, y2: int):
		self.canvas.create_rectangle(x1, self.flip(y1), x2, self.flip(y2), fill=self.color, wdth=0)

	def drawPalette(self):
		for i in range(len(self.colors)):
			self.setColor(idx = i)
			self.moveTo(10, 10+i)
			self.horzLineTo(200)

