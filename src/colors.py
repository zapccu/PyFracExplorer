
import numpy as np
import math
import colorsys

#
# Color conversion functions
#
# A rgb value is a numpy array of type uint8 with 3 elements (red, green, blue)
#

# Construct rgb value
def rgb(red: int, green: int, blue: int) -> np.ndarray:
	return np.asarray([red, green, blue], dtype=np.uint8)

# Convert rgb value to html color string
def rgbToStr(rgb: np.ndarray) -> str:
	return '#{:02X}{:02X}{:02X}'.format(rgb[0], rgb[1], rgb[2])

# Convert integer value to rgb value
def intToRGB(intColor: int) -> np.ndarray:
	return np.asarray(((intColor >> 16) & 0xFF, (intColor >> 8) & 0xFF, intColor & 0xFF), dtype=np.uint8)

# Convert rgb value to integer value
def rgbToInt(rgb: np.ndarray) -> int:
	return (int(rgb[2]) & 0xFF) | ((int(rgb[1]) & 0xFF) << 8) | ((int(rgb[0]) & 0xFF) << 16)

def hlsToRGB(hls: tuple[float, float, float]) -> np.ndarray:
	r, g, b = colorsys.hls_to_rgb(*hls)
	return (np.asarray([r, g, b])*255).astype(np.uint8)
	
def hsvToRGB(hsv: tuple[float, float, float]) -> np.ndarray:
	r, g, b = colorsys.hsv_to_rgb(*hsv)
	return (np.asarray([r, g, b])*255).astype(np.uint8)	

# Blinn Phong shading
# Taken from https://github.com/jlesuffleur/gpu_mandelbrot/blob/master/mandelbrot.py
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


"""
	Color palettes

	Color palettes are numpy arrays of type uin8 with shape (n,3).
	They contain at least 3 elements: first, last and default color.
	The default color is stored at the end of the array in element n-1.
	An array row contains the red, green and blue part of a color.
"""

#
# Create color palettes
#

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

#
# Map calculation results to color
#

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
	startColor = rgbToInt(palette[0])
	endColor   = rgbToInt(palette[1])
	return intToRGB(int((endColor-startColor)/maxValue*value))
