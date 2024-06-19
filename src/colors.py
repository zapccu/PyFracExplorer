
import re

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
		self.rgb = (int(blue) & 0xFF) | ((int(green) & 0xFF) << 8) | ((int(red) & 0xFF) << 16)
	def getRGB(self):
		return(self.red(), self.green(), self.blue())
	
	def blue(self):
		return self.rgb & 0xFF
	def green(self):
		return (self.rgb >> 8) & 0xFF
	def red(self):
		return (self.rgb >> 16) & 0xFF
	
	def rgbStr(self) -> str:
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
	def maxColors(self) -> int:
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

		print(endColor)
		print("0 = " + str(self.colors[0]))
		print("99 = " + str(self.colors[-1]))

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