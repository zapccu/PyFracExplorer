
from fractal import *

class Color:
	# Color value. Integer encoded as 0x00RRGGBB
	rgb = 0

	def __init__(self, red, green, blue):
		self.setRGB(red, green, blue)

	def __repr__(self) -> str:
		return f"Color({self.red()}, {self.green()}, {self.blue()})"
	def __str__(self) -> str:
		return self.rgbStr()
	
	def __eq__(self, value: object) -> bool:
		return self.rgb == value.rgb
	def __ne__(self, value: object) -> bool:
		return self.rgb != value.rgb
	
	def setRGB(self, red: int, green: int, blue: int):
		self.rgb = (int(blue) & 0xFF) & ((int(green) & 0xFF) << 8) & ((int(red) & 0xFF) << 16)
	def getRGB(self):
		return(self.red(), self.green(), self.blue())
	
	def blue(self):
		return self.rgb & 0xFF
	def green(self):
		return (self.rgb >> 8) & 0xFF
	def red(self):
		return (self.rgb >> 16) & 0xFF
	
	def rgbStr(self):
		return '#{:02X}{:02X}{:02X}'.format(int(self.red()), int(self.green()), int(self.blue()))


class ColorTable:

	colors = [ Color(255, 255, 255) ]
	defColor = Color(0, 0, 0)

	def __init__(self, defColor=Color(0, 0, 0)):
		self.defColor = defColor

	# Return color table entry
	# If key is out of range, the default color is returned
	def getColor(self, idx):
		if idx >= len(self.colors) or idx < 0:
			return self.defColor
		else:
			return self.colors[idx]

	def getModColor(self, value):
		return self.colors[value % len(self.colors)]
	
	def getMapColor(self, value, maxValue):
		if value >= maxValue:
			return self.defColor
		else:
			return self.colors[int(len(self.colors)/maxValue*value)]
	
	# Return maximum number of colors
	def maxColors(self):
		return len(self.colors)
	
	# Set default color
	def setDefColor(self, color: Color):
		self.defColor = color

	def add(self, colorTable):
		if self.colors[-1] == colorTable.colors[0]:
			self.colors.append(colorTable.colors[1:])
		else:
			self.colors.append(colorTable.colors)

	# Create a smooth, linear color table
	def createLinearTable(self, numColors: int, startColor: Color, endColor: Color, modFlags: Color = Color(1, 1, 1)):
		numColors = max(numColors, 2)
		self.colors = [Color(0, 0, 0)] * numColors
		self.colors[0] = startColor
		self.colors[-1] = endColor

		cRed, cGreen, cBlue = startColor.getRGB()
		distRed, distGreen, distBlue = (
			(endColor.red()-startColor.red())/(numColors-1)*modFlags.red(),
			(endColor.green()-startColor.green())/(numColors-1)*modFlags.green(),
			(endColor.blue()-startColor.blue())/(numColors-1)*modFlags.blue()
		)

		for i in range(1, numColors-1):
			cRed += distRed
			cGreen += distGreen
			cBlue += distBlue
			self.colors[i] = Color(cRed, cGreen, cBlue)



class Graphics:

	# Drawing canvas
	canvas = None

	# Flip vertical orientation
	flipY = False

	# Color palette
	colors = ColorTable()

	# Current color
	color = '#ffffff'

	# Current color index
	colorIdx = 0

	# Current drawing position
	x = 0
	y = 0

	def flip(self, y):
		if self.flipY:
			return self.height-y-1
		else:
			return y

	def __init__(self, canvas, width, height, flipY = False):
		self.canvas = canvas
		self.width = width
		self.height = height
		self.flipY = flipY
		self.setColor(0)

	def moveTo(self, x, y):
		self.x = x
		self.y = y

	# Set color palette
	def setColorTable(self, colorTable):
		self.colors = colorTable

	# Set color to palette index
	def setColor(self, color):
		if type(color) == int:
			self.colorIdx = color
			self.color = self.colors.getColor(color).rgbStr()
		else:
			self.color = color.rgbStr()

	# Draw a horizontal line excluding end point
	# Set cursor to end point
	def horzLineTo(self, x):
		if x >= 0 and x != self.x:
			if x > self.x:
				self.canvas.create_line(self.x, self.flip(self.y), x-1, self.flip(self.y), fill=self.color, width=1)
			else:
				self.canvas.create_line(self.x, self.flip(self.y), x+1, self.flip(self.y), fill=self.color, width=1)
			self.x = x

	# Draw vertical line excluding end point
	# Set cursor to end point
	def vertLineTo(self, y):
		if y >= 0 and y != self.y:
			if y > self.y:
				self.canvas.create_line(self.x, self.flip(self.y), self.x, self.flip(y-1), fill=self.color, width=1)
			else:
				self.canvas.create_line(self.x, self.flip(self.y), self.x, self.flip(y+1), fill=self.color, width=1)
			self.y = y

	# Draw a filled rectangle
	def fillRect(self, x1, y1, x2, y2):
		self.canvas.create_rectangle(x1, self.flip(y1), x2, self.flip(y2), fill=self.color, outline=self.color)

	def drawLineByLine(self, fractal: Fractal):
		for y in range(self.height):
			self.moveTo(0, y)
			cx, cy = fractal.mapXY(0, y)
			r = fractal.iterate(cx, cy)
			color = self.colors.getMapColor(r[0], fractal.getMaxValue())

			for x in range(1, self.width):
				cx, cy = fractal.mapXY(x, y)
				r = fractal.iterate(cx, cy)
				newColor = self.colors.getMapColor(r[0], fractal.getMaxValue())
				if newColor != color:
					self.setColor(color)
					self.horzLineTo(x)
					color = newColor

			self.setColor(color)
			self.horzLineTo(self.width)

