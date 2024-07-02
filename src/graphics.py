
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

		self.moveTo(0, 0)
		self.setColor(intColor = 0xFFFFFF)

	# Flip vertical coordinates
	def flip(self, y: int) -> int:
		if self.flipY:
			return self.height-y-1
		else:
			return y
		
	# Flip coordinates of line or rectangle
	def flip2(self, y1: int, y2: int) -> list[int]:
		if self.flipY:
			return (self.height-y2, self.height-y1)
		else:
			return (y1, y2)

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

	# Set drawing color to specified color
	def setColor(self, color: Color = None, strColor: str = '', intColor: int = Color.NOCOLOR):
		if color is not None:
			self.color = Color.rgbStr(color)
		elif strColor != '':
			self.color = strColor
		elif intColor != Color.NOCOLOR:
			self.color = Color.rgbStr(intColor)
		else:
			self.color = '#ffffff'

	# Draw a horizontal line excluding end point
	# Set drawing position to end point
	def horzLineTo(self, x: int):
		if x >= 0 and x != self.x:
			y = self.flip(self.y)
			# self.canvas.create_line(self.x, y, x, y, fill=self.color, width=1, capstyle=PROJECTING)
			self.canvas.create_rectangle(self.x, y, x, y, fill=self.color, width=0)
			self.x = x

	# Draw vertical line excluding end point
	# Set drawing position to end point
	def vertLineTo(self, y: int):
		if y >= 0 and y != self.y:
			y1, y2 = self.flip2(self.y, y)
			# self.canvas.create_line(self.x, y1, self.x, y2, fill=self.color, width=1, capstyle=PROJECTING)
			self.canvas.create_rectangle(self.x, y1, self.x, y2, fill=self.color, width=0)
			self.y = y

	def lineTo(self, x: int, y: int):
		if x >= 0 and y >= 0 and (x != self.x or y != self.y):
			self.canvas.create_line(self.x, self.flip(self.y), x, self.flip(y), fill=self.color, width=1, capstyle=PROJECTING)
			self.x = x
			self.y = y

	# Draw a filled rectangle excluding right and bottom line
	# Drawing position is not updated
	def fillRect(self, x1: int, y1: int, x2: int, y2: int):
		y11, y22 = self.flip2(y1, y2)
		self.canvas.create_rectangle(x1, y11, x2, y22, fill=self.color, width=0)

	def drawPalette(self):
		for i in range(len(self.colors)):
			self.setColor(idx = i)
			self.moveTo(10, 10+i)
			self.horzLineTo(200)

