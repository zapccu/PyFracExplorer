
import numpy as np
import math

from numba import njit


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

# Convert hsl to rgb
@njit(cache=True)
def hslToRGB(hue: float, saturation: float, lightness: float) -> np.ndarray:
	if saturation == 0:
		return (np.asarray([lightness, lightness, lightness]) * 255).astype(np.uint8)
	
	q = lightness * (1 + saturation) if lightness < 0.5 else lightness + saturation - lightness * saturation
	p = 2 * lightness - q

	r = int(_hueToRgb(p, q, hue + 1/3) * 255)
	g = int(_hueToRgb(p, q, hue) * 255)
	b = int(_hueToRgb(p, q, hue - 1/3) * 255)

	return np.asarray([r, g, b]).astype(np.uint8)

@njit(cache=True)
def _hueToRgb(p, q, t):
	if t < 0: t += 1
	if t > 1: t -= 1
	if t < 1/6: return p + (q - p) * 6 * t
	if t < 1/2: return q
	if t < 2/3: return p + (q - p) * (2/3 - t) * 6
	return p

# Convert hsb to rgb
@njit(cache=True)
def hsbToRGB(hue: float, saturation: float, brightness: float) -> np.ndarray:
	if saturation == 0.0:
		return np.asarray([int(brightness*255), int(brightness*255), int(brightness*255)]).astype(np.uint8)
	i = int(hue * 6.0)
	f = (hue * 6.0) - i
	p = int(brightness * (1.0 - saturation) * 255)
	q = int(brightness * (1.0 - saturation * f) * 255)
	t = int(brightness * (1.0 - saturation * (1.0 - f)) * 255)
	v = int(brightness * 255)
	i = i % 6
	if i == 0: return np.asarray([v, t, p]).astype(np.uint8)
	if i == 1: return np.asarray([q, v, p]).astype(np.uint8)
	if i == 2: return np.asarray([p, v, t]).astype(np.uint8)
	if i == 3: return np.asarray([p, q, v]).astype(np.uint8)
	if i == 4: return np.asarray([t, p, v]).astype(np.uint8)
	if i == 5: return np.asarray([v, p, q]).astype(np.uint8)

# Blinn Phong shading
#  light:
#    0 =
#    1 =
#    2 =
#    3 = ambiant
#    4 = diffuse
#    5 = specular
#    6 = shininess
#
@njit(cache=True)
def phong(normal: complex, light):
	## Lambert normal shading (diffuse light)
	normal /= abs(normal)    

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

def createLinearPalette(numColors: int, colorPoints: list = [(255, 255, 255)], defColor: tuple = (0, 0, 0)) -> np.ndarray:
	if len(colorPoints) == 0:
		# Greyscale palette
		palette = np.linspace((0, 0, 0), (255, 255, 255), max(numColors, 2), dtype=np.uint8)
	elif (len(colorPoints) == 1):
		# Monochrome palette
		palette = np.full((max(numColors,1),3), colorPoints[0], dtype=np.uint8)
	else:
		numColors = max(numColors,len(colorPoints))
		secSize = int(numColors/(len(colorPoints)-1))
		palette = np.array([colorPoints[0]], dtype=np.uint8)
		for i in range(len(colorPoints)-1):
			if secSize + len(palette)-1 > numColors: secSize = numColors - len(palette)
			palette = np.vstack((palette[:-1], np.linspace(colorPoints[i], colorPoints[i+1], secSize, dtype=np.uint8)))

	# Append default color and return palette
	return np.vstack((palette, np.array(defColor, dtype=np.uint8)))
	
def createRGBPalette(numColors: int, startColor: tuple, endColor: tuple, defColor: tuple = (0, 0, 0)) -> np.ndarray:
	return np.array([startColor, endColor, defColor], dtype=np.uint8)

def createSinusPalette(numColors: int, thetas: list = [.85, .0, .15], defColor: tuple = (0, 0, 0)) -> np.ndarray:
	numColors = max(numColors, 2)
	ct = np.linspace(0, 1, numColors)
	colors = np.column_stack(((
		ct + thetas[0]) * 2 * math.pi,
		(ct + thetas[1]) * 2 * math.pi,
		(ct + thetas[2]) * 2 * math.pi)
	)
	return np.vstack((((0.5 + 0.5 * np.sin(colors)) * 255).astype(np.uint8, copy=False), np.array(defColor, dtype=np.uint8)))

def createSinusCosinusPalette(numColors: int, defColor: tuple = (0, 0, 0)):
	ct = np.arange(0, numColors)
	colors = np.column_stack((
		ct/(numColors-1),
		(np.cos(ct * 0.1) + 1.0) * 0.5,
		(np.sin(ct * 0.01) + 1.0) * 0.5)
	)
	return np.vstack(((colors * 255).astype(np.uint8, copy=False), np.array(defColor, dtype=np.uint8)))

#
# Map calculation results to color
#

# Colorization modes
_C_ITERATIONS = 0
_C_DISTANCE   = 1
_C_POTENTIAL  = 2
_C_SHADING    = 3
_C_BLINNPHONG = 4

# Colorization flags
_F_LINEAR  = 1
_F_MODULO  = 2
_F_ORBITS  = 4   # Colorize orbits
_F_STRIPES = 8
_F_HUE     = 16

orbitColors = np.array([
			[ 255, 0, 0 ],
			[ 255, 255, 0 ],
			[ 0, 255, 255 ],
			[ 0, 255, 0 ],
			[ 0, 0, 255 ],
			[ 255, 0, 0 ],
			[ 255, 255, 0 ],
			[ 0, 255, 255 ],
			[ 0, 255, 0 ],
			[ 0, 0, 255 ]
], dtype=np.uint8)

# Map iteration result to color depending on mapping method
@njit(cache=True)
def mapColorValue(palette: np.ndarray, value: float, maxValue: int, colorize: int = 0, flags: int = 1) -> np.ndarray:
	pLen = len(palette)-1

	if colorize == _C_ITERATIONS:
		if value == maxValue: return palette[pLen]
		if flags & _F_LINEAR:
			return palette[int(value)] if maxValue == pLen else palette[int(pLen / maxValue * value)]
		elif flags & _F_MODULO:
			return palette[int(value)] if maxValue == pLen else palette[int(value) % pLen]
		elif flags & _F_HUE:
			h = math.pow((value/maxValue) * 360, 1.5) % 360
			return hsbToRGB(h/360, 1.0, 1.0)
	elif colorize == _C_DISTANCE:
		return palette[pLen] if value == 0 else palette[int(value * pLen)]
	elif colorize == _C_POTENTIAL:
		return np.array([0, 0, 0], dtype=np.uint8)
	elif colorize == _C_SHADING or colorize == _C_BLINNPHONG:
		c = int(255 * value)
		return np.array([c, c, c], dtype=np.uint8)
	else:
		return np.array([0, 0, 0], dtype=np.uint8)

@njit(cache=True)
def mapColorValueNew(palette: np.ndarray, values: np.ndarray, maxValue: int, colorize: int = 0, flags: int = 1) -> np.ndarray:
	pLen = len(palette)-1
	
	if colorize == _C_ITERATIONS:
		if flags & _F_LINEAR:
			if values[0] == maxValue: return palette[pLen]
			return palette[int(values[0])] if maxValue == pLen else palette[int(pLen / maxValue * values[0])]
		elif flags & _F_MODULO:
			if values[0] == maxValue: return palette[pLen]
			return palette[int(values[0])] if maxValue == pLen else palette[int(values[0]) % pLen]
	elif colorize == _C_DISTANCE:
		return palette[pLen] if values[1] == 0 else palette[int(values[1] * pLen)]
	elif colorize == _C_POTENTIAL:
		return np.array([0, 0, 0], dtype=np.uint8)




"""
	elif method == 2:
		startCol = rgbToInt(palette[0])
		endCol   = rgbToInt(palette[1])
		return intToRGB(startCol + int((endCol - startCol) / maxValue * value))

"""