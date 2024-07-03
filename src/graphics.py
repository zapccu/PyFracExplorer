
from tkinter import *

import numpy as np
import PIL
from PIL import Image as Img
from PIL import ImageTk

from fractal import *
from colors import *
from gui import *

"""
Class for graphic operations
"""

class Graphics:

	def __init__(self, drawFrame: DrawFrame, flipY = False, inMemory = False):
		self.drawFrame = drawFrame
		self.canvas    = drawFrame.canvas
		self.width     = drawFrame.canvasWidth
		self.height    = drawFrame.canvasHeight
		self.flipY     = flipY
		self.inMemory  = inMemory

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
		if self.inMemory:
			self.imageMap = np.zeros([height, width, 3], dtype=np.uint8)
		return True

	def endDraw(self):
		if self.inMemory:
			self.image = Img.fromarray(self.imageMap, 'RGB')
			self.tkImage = ImageTk.PhotoImage(self.image)
			self.image.save("test.png", "png")
			self.canvas.create_image(0, 0, image=self.tkImage, state='normal', anchor='nw')
			self.canvas.update()
		return
	
	# Set drawing position
	def moveTo(self, x: int, y: int):
		self.x = x
		self.y = y

	# Set drawing color to specified color
	def setColor(self, color: Color = None, strColor: str = '', intColor: int = Color.NOCOLOR):
		if color is not None:
			self.color    = Color.rgbStr(color)
			self.rgbColor = color.getRGB()
		elif strColor != '':
			self.color    = strColor
			self.rgbColor = Color.strRGB(strColor)
		elif intColor != Color.NOCOLOR:
			self.color    = Color.rgbStr(intColor)
			self.rgbColor = Color.intRGB(intColor)
		else:
			self.color    = '#ffffff'
			self.rgbColor = [ 255, 255, 255 ]

	# Draw a horizontal line excluding end point
	# Set drawing position to end point
	def horzLineTo(self, x: int):
		if x >= 0 and x != self.x:
			y = self.flip(self.y)
			if self.inMemory:
				self.imageMap[y, self.x:x] = self.rgbColor
			else:
				self.canvas.create_rectangle(self.x, y, x, y, fill=self.color, width=0)
			self.x = x

	# Draw vertical line excluding end point
	# Set drawing position to end point
	def vertLineTo(self, y: int):
		if y >= 0 and y != self.y:
			y1, y2 = self.flip2(self.y, y)
			if self.inMemory:
				self.imageMap[y1:y2, self.x] = self.rgbColor
			else:
				self.canvas.create_rectangle(self.x, y1, self.x, y2, fill=self.color, width=0)
			self.y = y

	def lineTo(self, x: int, y: int):
		if not self.inMemory and x >= 0 and y >= 0 and (x != self.x or y != self.y):
			self.canvas.create_line(self.x, self.flip(self.y), x, self.flip(y), fill=self.color, width=1, capstyle=PROJECTING)
			self.x = x
			self.y = y

	# Draw a filled rectangle excluding right and bottom line
	# Drawing position is not updated
	def fillRect(self, x1: int, y1: int, x2: int, y2: int):
		y11, y22 = self.flip2(y1, y2)
		if self.inMemory:
			self.imageMap[y11:y22, x1:x2] = self.rgbColor
		else:
			self.canvas.create_rectangle(x1, y11, x2, y22, fill=self.color, width=0)

	def drawPalette(self):
		for i in range(len(self.colors)):
			self.setColor(idx = i)
			self.moveTo(10, 10+i)
			self.horzLineTo(200)

