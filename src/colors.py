

class Color:
	
	NOCOLOR  = 0xFFFFFFFF
	MAXCOLOR = 0xFFFFFF

	def __init__(self, red = 0, green = 0, blue = 0):
		self.setRGB(red, green, blue)

	def __repr__(self) -> str:
		return f"Color({self.red()}, {self.green()}, {self.blue()})"
	def __str__(self) -> str:
		return Color.rgbStr(self.rgb)
	
	def __eq__(self, value: object) -> bool:
		return self.rgb == value.rgb
	def __ne__(self, value: object) -> bool:
		return self.rgb != value.rgb
	
	def setRGB(self, red: int, green: int, blue: int):
		self.rgb = (int(blue) & 0xFF) | ((int(green) & 0xFF) << 8) | ((int(red) & 0xFF) << 16)
	def getRGB(self):
		return(self.red(), self.green(), self.blue())
	
	def blue(self):
		return self.rgb & 0xFF
	def green(self):
		return (self.rgb >> 8) & 0xFF
	def red(self):
		return (self.rgb >> 16) & 0xFF
	
	@staticmethod
	def rgbStr(value) -> str:
		if type(value) == Color:
			return '#{:06X}'.format(value.rgb)
		elif type(value) == int:
			return '#{:06X}'.format(value)
		else:
			return '#000000'


class ColorLine:

	def __init__(self, colors: list = []):
		self.line = colors
		if len(colors) > 0:
			self.unique = len(set(colors)) == 1
		else:
			self.unique = False

	def __iadd__(self, color: int):
		if color >= 0 and color <= Color.MAXCOLOR:
			if len(self.line) == 0:
				# First entry, unique color
				self.unique = True
			else:
				if self.unique and color != self.line[0]:
					self.unique = False
			self.line.append(color)
		return self

	def __len__(self):
		return len(self.line)
	
	def __getitem__(self, index):
		if index >= 0 and index < len(self.line):
			return self.line[index]
		else:
			return Color.NOCOLOR
				
	def isUnique(self):
		return self.unique
		
	def __eq__(self, b):
		return self.isUnique() and b.isUnique() and self.line[0] == b.line[0]
	
	# Split a color line into 2 new color lines
	def split(self):
		mid = int(len(self.line)/2)
		if mid > 0:
			return ColorLine(self.line[:mid]), ColorLine(self.line[mid:])
		else:
			return None
	
class ColorTable:

	def __init__(self, color = Color(255, 255, 255), defColor = Color(0, 0, 0)):
		self.colors = []
		self.defColor = defColor

	# Return color table entry
	# If key is out of range, the default color is returned
	def __getitem__(self, idx) -> Color:
		if idx >= len(self.colors) or idx < 0:
			return self.defColor
		else:
			return self.colors[idx]

	def getModColor(self, value) -> Color:
		return self.colors[value % len(self.colors)]
	
	def getMapColor(self, value, maxValue) -> Color:
		if value >= maxValue:
			return self.defColor
		else:
			return self.colors[int(len(self.colors)/maxValue*value)]
	
	# Return maximum number of colors
	def __len__(self):
		return len(self.colors)
	
	# Set default color
	def setDefColor(self, color: Color):
		self.defColor = color

	# Append color table
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