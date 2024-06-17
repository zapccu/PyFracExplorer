

class Color:
	_rgb_ = (0, 0, 0)

	def __init__(self, rgb=(0, 0, 0)):
		self._rgb_ = rgb

	def __init__(self, red, green, blue):
		self._rgb_ = (red, green, blue)

	def __eq__(self, color):
		if self._rgb_ == color.rgb:
			return True
		else:
			return False

	def red(self):
		return self._rgb_[0]
	def green(self):
		return self._rgb_[1]
	def blue(self):
		return self._rgb_[2]
	def rgb(self):
		return self._rgb_
	def rgbStr(self):
		return '#{:02X}{:02X}{:02X}'.format(int(self._rgb_[0]), int(self._rgb_[1]), int(self._rgb_[2]))


class ColorTable:

	colors = [ Color(255, 255, 255) ]
	defColor = Color(0, 0, 0)

	def __init__(self, defColor=Color(0, 0, 0)):
		self.defColor = defColor

	# Return color table entry
	# If key is out of range, the default color is returned
	def __getitem__(self, key):
		if key >= len(self.colors) or key < 0:
			return self.defColor
		else:
			return self.colors[key]

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

		(cRed, cGreen, cBlue) = startColor.rgb()
		(distRed, distGreen, distBlue) = (
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

	# Color palette
	colors = ColorTable()

	# Current color
	color = '#ffffff'

	# Current color index
	colorIdx = 0

	# Current drawing position
	x = 0
	y = 0

	def __init__(self, canvas):
		self.canvas = canvas
		self.setColor(0)

	def moveTo(self, x, y):
		self.x = x
		self.y = y

	# Set color palette
	def setColorTable(self, colorTable):
		self.colors = colorTable

	# Set color to palette index
	def setColor(self, colorIdx):
		self.colorIdx = colorIdx
		self.color = self.colors[colorIdx].rgbStr()

	# Draw a horizontal line excluding end point
	# Set cursor to end point
	def horzLineTo(self, x):
		if x >= 0 and x != self.x:
			if x > self.x:
				self.canvas.create_line((self.x, self.y), (x-1, self.y), fill=self.color, width=1)
			else:
				self.canvas.create_line((self.x, self.y), (x+1, self.y), fill=self.color, width=1)
			self.x = x

	# Draw vertical line excluding end point
	# Set cursor to end point
	def vertLineTo(self, y):
		if y >= 0 and y != self.y:
			if y > self.y:
				self.canvas.create_line((self.x, self.y), (self.x, y-1), fill=self.color, width=1)
			else:
				self.canvas.create_line((self.x, self.y), (self.x, y+1), fill=self.color, width=1)
			self.y = y

	# Draw a filled rectangle
	def fillRect(self, x1, y1, x2, y2):
		self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.color, outline=self.color)

