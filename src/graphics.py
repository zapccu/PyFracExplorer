

class Color:
	rgb = (0, 0, 0)

	def __init__(self, rgb=(0, 0, 0)):
		self.rgb = rgb

	def red(self):
		return self.rgb[0]
	def green(self):
		return self.rgb[1]
	def blue(self):
		return self.rgb[2]
	def rgb(self):
		return self.rgb
	def rgbStr(self):
		return '#{:02x}{:02x}{:02x}'.format(self.rgb[0], self.rgb[1], self.rgb[2])


class ColorTable:

	colors = [ Color(255, 255, 255) ]
	defColor = Color(0, 0, 0)

	def __init__(self, defColor=Color(0, 0, 0)):
		self.defColor = defColor

	def __getitem__(self, key):
		if key >= len(self.colors) or key < 0:
			return self.defColor
		else:
			return self.colors[key]
		
	def setDefColor(self, color):
		self.defColor = color


class LinearColorTable(ColorTable):

	def __init__(self, numColors, startColor: Color, endColor: Color, modFlags: Color):
		ColorTable.__init__(self)

		numColors = max(numColors, 2)
		self.colors = [Color(0, 0, 0)] * numColors
		self.colors[0] = startColor
		self.colors[-1] = endColor

		(cRed, cGreen, cBlue) = startColor.rgb()
		(distRed, distGreen, distBlue) = (
			(endColor.red-startColor.red)/(numColors-1)*modFlags.red(),
			(endColor.green-startColor.green)/(numColors-1)*modFlags.green(),
			(endColor.blue-startColor.blue)/(numColors-1)*modFlags.blue()
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

	# Current drawing position
	x = 0
	y = 0

	def __init__(self, canvas):
		self.canvas = canvas

	def moveTo(self, x, y):
		self.x = x
		self.y = y

	# Set color palette
	def setColorTable(self, colorTable):
		self.colors = colorTable

	# Set color to palette index
	def setColor(self, colorIdx):
		self.color = self.colors[colorIdx].rgbStr()

	def horzLineTo(self, x):
		self.canvas.create_line((self.x, self.y), (x, self.y), fill=self.color, width=1)

	def vertLineTo(self, y):
		self.canvas.create_line((self.x, self.y), (self.x, y), fill=self.color, width=1)

	def fillRect(self, x1, y1, x2, y2):
		self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.color, outline=self.color)

