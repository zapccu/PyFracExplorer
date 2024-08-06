
import numpy as np
import math
import colorsys

class Color:
	
	NOCOLOR  = 0xFFFFFFFF
	MAXCOLOR = 0xFFFFFF

	def __init__(self, red = 0, green = 0, blue = 0, intColor: int = NOCOLOR,
			  rgb = None, hls: tuple[float,float,float] = None, hsv: tuple[float,float,float] = None):
		if intColor != Color.NOCOLOR:
			self.rgb = Color.intToRGB(intColor)
		elif rgb is not None:
			self.rgb = rgb
		elif hls is not None:
			self.rgb = Color.hlsToRGB(hls)
		elif hsv is not None:
			self.rgb = Color.hsvToRGB(hsv)
		else:
			self.rgb = np.asarray([red, green, blue], dtype=np.uint8)

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
		
	@staticmethod
	def intToRGB(intColor: int) -> np.ndarray:
		return np.asarray(((intColor >> 16) & 0xFF, (intColor >> 8) & 0xFF, intColor & 0xFF), dtype=np.uint8)

	@staticmethod	
	def rgbToInt(rgb: np.ndarray) -> int:
		return (int(rgb[2]) & 0xFF) | ((int(rgb[1]) & 0xFF) << 8) | ((int(rgb[0]) & 0xFF) << 16)

	@staticmethod
	def hlsToRGB(hls: tuple[float, float, float]) -> np.ndarray:
		r, g, b = colorsys.hls_to_rgb(*hls)
		return (np.asarray([r, g, b])*255).astype(np.uint8)
	
	@staticmethod
	def hsvToRGB(hsv: tuple[float, float, float]) -> np.ndarray:
		r, g, b = colorsys.hsv_to_rgb(*hsv)
		return (np.asarray([r, g, b])*255).astype(np.uint8)	

class CalcColor:

	@staticmethod
	def mapSinusCosinus (value: int, maxValue: int) -> np.ndarray:
		r = value / (maxValue-1)
		g = (math.cos(value * 0.1) + 1.0) * 0.5,
		b = (math.sin(value * 0.01) + 1.0) * 0.5
		return np.asarray([int(r*255), int(g*255), int(b*255)], dtype=np.uint8)

	@staticmethod
	def mapSinus(value: int, maxValue: int, theta = [.85, .0, .15]) -> np.ndarray:
		f = 1.0/(maxValue-1)
		x = min(value * f, 1.0)
		r = 0.5 + 0.5 * math.sin((x + theta[0]) * 2 * math.pi)
		g = 0.5 + 0.5 * math.sin((x + theta[1]) * 2 * math.pi)
		b = 0.5 + 0.5 * math.sin((x + theta[2]) * 2 * math.pi)
		return np.asarray([int(r*255), int(g*255), int(b*255)], dtype=np.uint8)

	# Blinn Phong shading
	# Taken from https://github.com/jlesuffleur/gpu_mandelbrot/blob/master/mandelbrot.py
	@staticmethod
	def phong(normal: complex, light: list[float]):
		## Lambert normal shading (diffuse light)
		normal = normal / abs(normal)    
    
		# theta: light angle; phi: light azimuth
		# light vector: [cos(theta)cos(phi), sin(theta)cos(phi), sin(phi)]
		# normal vector: [normal.real, normal.imag, 1]
		# Diffuse light = dot product(light, normal)
		ldiff = (normal.real * math.cos(light[0]) * math.cos(light[1]) +
			normal.imag * math.sin(light[0]) * math.cos(light[1]) + 
			1 * math.sin(light[1]))
		# Normalization
		ldiff = ldiff / (1 + 1 * math.sin(light[1]))

		## Specular light: Blinn Phong shading
		# Phi half: average between phi and pi/2 (viewer azimuth)
		# Specular light = dot product(phi_half, normal)
		phi_half = (math.pi / 2 + light[1]) / 2
		lspec = (normal.real * math.cos(light[0]) * math.sin(phi_half) +
			normal.imag * math.sin(light[0]) * math.sin(phi_half) +
			1 * math.cos(phi_half))
		# Normalization
		lspec = lspec / (1 + 1 * math.cos(phi_half))
		#spec_angle = max(0, spec_angle)
		lspec = lspec ** light[6] # shininess

		## Brightness = ambiant + diffuse + specular
		bright = light[3] + light[4]*ldiff + light[5]*lspec
		## Add intensity
		bright = bright * light[2] + (1-light[2])/2

		return bright


class ColorTable:

	def __init__(self, colors = [ Color(255, 255, 255) ], defColor = Color(0, 0, 0)):
		self.colors   = colors
		self.defColor = defColor

	def getDefColor(self) -> np.ndarray:
		return self.defColor.rgb

	def __str__(self) -> str:
		return ','.join(map(str, self.colors))
	
	# Return color table entry as rgb value
	# If key is out of range, the default color is returned
	def __getitem__(self, idx: int) -> np.ndarray:
		return self.getColor(idx)

	# Return color table entry
	# If key is out of range, the default color is returned
	def getColor(self, idx: int) -> np.ndarray:
		if idx >= len(self.colors) or idx < 0:
			return self.defColor.rgb
		else:
			return self.colors[idx].rgb
	
	# Map value to palette entry (linear)
	def mapValueLinear(self, value: int, maxValue: int) -> np.ndarray:
		if value >= maxValue or value < 0:
			return self.defColor.rgb
		
		idx = int(len(self.colors)/(maxValue-1)*value)
		idx = min(max(idx, 0), len(self.colors)-1)

		return self.colors[idx].rgb
	
	# Map value to palette entry (modulo division)
	def mapValueModulo(self, value: int, maxValue: int) -> np.ndarray:
		if value >= maxValue or value < 0:
			return self.defColor.rgb
		
		idx = value % len(self.colors)
		return self.colors[idx].rgb
	
	# Map value to RGB value (palette is ignored)
	def mapValueRGB(self, value: int, maxValue: int) -> np.ndarray:
		if value >= maxValue or value < 0:
			return self.defColor.rgb
		
		return Color.intToRGB(int(0xFFFFFF / (maxValue-1) * value))
	
	# Return maximum number of colors (without default color)
	def __len__(self):
		return len(self.colors)

	# Append color table
	def add(self, colorTable):
		if self.colors[-1] == colorTable.colors[0]:
			self.colors.append(colorTable.colors[1:])
		else:
			self.colors.append(colorTable.colors)

	# Create a smooth, linear color table
	@staticmethod
	def createLinearTable(numColors: int, startColor: Color, endColor: Color, modFlags: Color = Color(1, 1, 1)):
		numColors = max(numColors, 2)
		colors = [Color(0, 0, 0)] * numColors
		colors[0] = startColor
		colors[-1] = endColor

		cRed, cGreen, cBlue = startColor.getRGB()
		distRed, distGreen, distBlue = (
			(endColor.red()-startColor.red())/(numColors-1)*modFlags.red(),
			(endColor.green()-startColor.green())/(numColors-1)*modFlags.green(),
			(endColor.blue()-startColor.blue())/(numColors-1)*modFlags.blue()
		)

		for i in range(1, numColors-1):
			cRed   += distRed
			cGreen += distGreen
			cBlue  += distBlue
			colors[i] = Color(cRed, cGreen, cBlue)

		return ColorTable(colors)

	@staticmethod
	def createSinusTable(numColors: int, theta = [.85, .0, .15]):
		numColors = max(numColors, 2)
		colors = [Color(0, 0, 0)] * numColors

		for i in range(0, numColors):
			colors[i] = Color(rgb=CalcColor.mapSinus(i, numColors, theta))

		return ColorTable(colors)

	@staticmethod
	def createSinusCosinusTable(numColors: int):
		numColors = max(numColors, 2)
		colors = [Color(0, 0, 0)] * numColors

		for i in range(0, numColors):
			colors[i] = Color(rgb=CalcColor.mapSinus(i, numColors))

"""
	Color palettes

	Color palettes are numpy arrays of type uin8 with shape (n,3).
	They contain at least 3 elements: first, last and default color.
	The default color is stored at the end of the array in element n-1.
	An array row contains the red, green and blue part of a color.
"""

# Create a smooth, linear color table
def createLinearPalette(numColors: int, startColor: tuple, endColor: tuple, defColor: tuple = (0, 0, 0)) -> np.ndarray:
	return np.append(np.linspace(startColor, endColor, max(numColors, 2), dtype=np.uint8), defColor)

def createRGBPalette(numColors: int, startColor: tuple, endColor: tuple, defColor: tuple = (0, 0, 0)) -> np.ndarray:
	return np.array([startColor, endColor, defColor])

def createSinusPalette(numColors: int, thetas: list = [.85, .0, .15], defColor: tuple = (0, 0, 0)) -> np.ndarray:
	numColors = max(numColors, 2)
	ct = np.linspace(0, 1, numColors)
	colors = np.column_stack(((
		ct + thetas[0]) * 2 * math.pi,
		(ct + thetas[1]) * 2 * math.pi,
		(ct + thetas[2]) * 2 * math.pi)
	)
	return np.append(((0.5 + 0.5 * np.sin(colors)) * 255).astype(np.uint8, copy=False), defColor)

def createSinusCosinusPalette(numColors: int, defColor: tuple = (0, 0, 0)):
	ct = np.arange(0, numColors)
	colors = np.column_stack((
		ct/(numColors-1),
		(np.cos(ct * 0.1) + 1.0) * 0.5,
		(np.sin(ct * 0.01) + 1.0) * 0.5)
	)
	return np.append((colors * 255).astype(np.uint8, copy=False), defColor)

# Map value to palette entry (linear)
def mapValueLinear(palette: np.ndarray, value: int, maxValue: int):
	pLen = len(palette)-1
	if value >= maxValue or value < 0:
		return palette[pLen]
	idx = value if pLen == maxValue else int(pLen/maxValue*value)
	return palette[idx]
	
# Map value to palette entry (modulo division)
def mapValueModulo(palette: np.ndarray, value: int, maxValue: int):
	pLen = len(palette)-1
	if value >= maxValue or value < 0:
		return palette[pLen]
	idx = value if pLen == maxValue else value % pLen
	return palette[idx]

def mapValueRGB(palette: np.ndarray, value: int, maxValue: int):
	if value >= maxValue or value < 0:
		return palette[2]
	startColor = Color.rgbToInt(palette[0])
	endColor   = Color.rgbToInt(palette[1])
	return Color.intToRGB(int((endColor-startColor)/maxValue*value))
