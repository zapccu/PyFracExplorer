
import numpy as np

class Color:
	
	NOCOLOR  = 0xFFFFFFFF
	MAXCOLOR = 0xFFFFFF

	def __init__(self, red = 0, green = 0, blue = 0, intColor: int = NOCOLOR, rgb = None):
		if intColor != Color.NOCOLOR:
			self.rgb = np.asarray(((intColor >> 16) & 0xFF, (intColor >> 8) & 0xFF, intColor & 0xFF), dtype=np.uint8)
		elif rgb is not None:
			self.rgb = rgb
		else:
			self.rgb = np.asarray([ red, green, blue], dtype=np.uint8)

	def __repr__(self) -> str:
		return f"Color({self.rgb[0]}, {self.rgb[1]}, {self.rgb[2]}"
	def __str__(self) -> str:
		return '#{:02X}{:02X}{:02X}'.format(self.rgb[0], self.rgb[1], self.rgb[2])
	
	def __int__(self):
		return (int(self.rgb[2]) & 0xFF) | ((int(self.rgb[1]) & 0xFF) << 8) | ((int(self.rgb[0]) & 0xFF) << 16)
	
	def __eq__(self, value: object) -> bool:
		return np.array_equal(self.rgb, value)
	def __ne__(self, value: object) -> bool:
		return not np.array_equal(self.rgb, value)
	
	def setRGB(self, red: int, green: int, blue: int):
		self.rgb = np.asarray([ red, green, blue], dtype=np.uint8)
	def getRGB(self) -> list[int]:
		return (self.rgb[0], self.rgb[1], self.rgb[2])
	
	def blue(self) -> int:
		return self.rgb[2]
	def green(self) -> int:
		return self.rgb[1]
	def red(self) -> int:
		return self.rgb[0]
	
	@staticmethod
	def rgbStr(value) -> str:
		if type(value) == Color:
			return str(value)
		elif type(value) == int:
			return '#{:06X}'.format(value)
		elif type(value) == np.ndarray and len(value) == 3:
			return '#{:02X}{:02X}{:02X}'.format(value[0], value[1], value[2])
		else:
			return '#000000'
	
class ColorTable:

	def __init__(self, colors = [ Color(255, 255, 255) ], defColor = Color(0, 0, 0)):
		self.colors = colors
		self.defColor = defColor

	# Return color table entry
	# If key is out of range, the default color is returned
	def __getitem__(self, idx) -> int:
		if idx >= len(self.colors) or idx < 0:
			return self.defColor
		else:
			return self.colors[idx].rgb
	
	# Return maximum number of colors
	def __len__(self):
		return len(self.colors)

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