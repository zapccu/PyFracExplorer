
from tkinter import *

import numpy as np
import PIL
from PIL import Image as Img
from PIL import ImageTk
# from skimage.draw import line, line_aa

import colors as col

"""
Class for graphic operations
"""

class Graphics:

	def __init__(self, canvas: object, flipY = False):
		self.canvas = canvas
		self.flipY  = flipY

		self.width  = self.canvas.winfo_reqwidth()
		self.height = self.canvas.winfo_reqheight()
		self.imageMap = np.zeros([self.height, self.width, 3], dtype=np.uint8)

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
			return (self.height-y2-1, self.height-y1-1)
		else:
			return (y1, y2)

	# Initialize drawing environment
	def beginDraw(self) -> bool:
		return True

	# Cleanup drawing environment, update canvas
	def endDraw(self):
		self.image = Img.fromarray(self.imageMap, 'RGB')
		self.tkImage = ImageTk.PhotoImage(self.image)
		# self.image.save("test.png", "png")
		self.canvas.create_image(0, 0, image=self.tkImage, state='normal', anchor='nw')
		self.canvas.update()
		return
	
	# Set drawing position
	def moveTo(self, x: int, y: int):
		self.x = x
		self.y = y

	# Set drawing color to specified color
	def setColor(self, rgb: np.ndarray):
		self.color    = col.rgbToStr(rgb)
		self.rgbColor = rgb

	# Draw a pixel
	def setPixelAt(self, x: int, y: int, rgb: np.ndarray | None = None):
		y = self.flip(y)
		self.imageMap[y, x] = self.rgbColor if rgb is None else rgb

	def getPixelAt(self, x: int, y: int) -> np.ndarray:
		y = self.flip(y)
		return self.imageMap[y, x]

	def isUnique(self, x1: int, y1: int, x2: int, y2: int) -> bool:
		if y1 == y2:
			y1 = self.flip(y1)
			return len(np.unique(self.imageMap[y1, x1:x2], axis = 0)) == 1
		else:
			y1, y2 = self.flip2(y1, y2)
			return len(np.unique(self.imageMap[y1:y2, x1], axis = 0)) == 1
		
	# Draw a horizontal line excluding end point
	# Set drawing position to end point
	def horzLineTo(self, x: int):
		if x >= 0 and x != self.x:
			y = self.flip(self.y)
			self.imageMap[y, self.x:x] = self.rgbColor
			self.x = x

	# Draw vertical line excluding end point
	# Set drawing position to end point
	def vertLineTo(self, y: int):
		if y >= 0 and y != self.y:
			y1, y2 = self.flip2(self.y, y)
			self.imageMap[y1:y2, self.x] = self.rgbColor
			self.y = y

	# Not implemented (and not needed)
	def lineTo(self, x: int, y: int):
		return

	# Draw a filled rectangle excluding right and bottom line
	# Drawing position is not updated
	def fillRect(self, x1: int, y1: int, x2: int, y2: int):
		y11, y22 = self.flip2(y1, y2)
		self.imageMap[y11:y22, x1:x2] = self.rgbColor

