
import math
import cmath

import numpy as np
import numba as nb


#
# Color conversion functions
#
# A rgb value is a numpy array of type float64 with 3 elements (red, green, blue)
# A rgbi value is a numpy array of type uint8 with 3 elements (red, green, blue)
#

# Construct a rgb value
def rgb(red: float, green: float, blue: float) -> np.ndarray:
	return np.asarray([red, green, blue], dtype=np.float64)

# Construct a rgbi value
def rgbi(red: int, green: int, blue: int) -> np.ndarray:
	return np.asarray([red, green, blue], dtype=np.uint8)

# Convert rgbi values to rgb values
def rgbf(red: int, green: int, blue: int) -> tuple[float, float, float]:
	return (red/255, green/255, blue/255)

# Convert rgb to rgbi
@nb.njit(cache=True)
def rgb2rgbi(rgb: np.ndarray) -> np.ndarray:
	return (rgb * 255).astype(np.uint8)

# Convert rgbi to rgb
def rgbi2rgb(rgbi: np.ndarray) -> np.ndarray:
	return (rgbi / 255).astype(np.float64)

# Convert rgbi value to html color string
def rgbi2str(rgb: np.ndarray) -> str:
	return '#{:02X}{:02X}{:02X}'.format(rgb[0], rgb[1], rgb[2])

# Convert integer value to rgb value
def int2rgbi(intColor: int) -> np.ndarray:
	return np.asarray(((intColor >> 16) & 0xFF, (intColor >> 8) & 0xFF, intColor & 0xFF), dtype=np.uint8)

# Convert rgb value to integer value
def rgbi2int(rgb: np.ndarray) -> int:
	return (int(rgb[2]) & 0xFF) | ((int(rgb[1]) & 0xFF) << 8) | ((int(rgb[0]) & 0xFF) << 16)

# Convert hsl to rgb
@nb.njit(cache=True)
def hsl2rgb(hue: float, saturation: float, lightness: float) -> np.ndarray:
	if saturation == 0:
		return np.asarray([lightness, lightness, lightness])
	
	q = lightness * (1 + saturation) if lightness < 0.5 else lightness + saturation - lightness * saturation
	p = 2 * lightness - q

	r = _hueToRgb(p, q, hue + 1/3)
	g = _hueToRgb(p, q, hue)
	b = _hueToRgb(p, q, hue - 1/3)

	return np.asarray([r, g, b], dtype=np.float64)

@nb.njit(cache=True)
def _hueToRgb(p, q, t):
	if t < 0: t += 1
	if t > 1: t -= 1
	if t < 1/6: return p + (q - p) * 6 * t
	if t < 1/2: return q
	if t < 2/3: return p + (q - p) * (2/3 - t) * 6
	return p

# Convert hsb to rgb
@nb.njit(cache=True)
def hsb2rgb(hue: float, saturation: float, brightness: float) -> np.ndarray:
	if saturation == 0.0:
		return np.asarray([brightness, brightness, brightness])
	i = int(hue * 6.0)
	f = (hue * 6.0) - i
	p = brightness * (1.0 - saturation)
	q = brightness * (1.0 - saturation * f)
	t = brightness * (1.0 - saturation * (1.0 - f))
	v = brightness
	i = i % 6
	if i == 0: return np.asarray([v, t, p], dtype=np.float64)
	if i == 1: return np.asarray([q, v, p], dtype=np.float64)
	if i == 2: return np.asarray([p, v, t], dtype=np.float64)
	if i == 3: return np.asarray([p, q, v], dtype=np.float64)
	if i == 4: return np.asarray([t, p, v], dtype=np.float64)
	if i == 5: return np.asarray([v, p, q], dtype=np.float64)

# Convert lch to rgb, luma = [0..1], chroma = [0..1], hue = [0..359]
# https://gist.github.com/cjgajard/743450e26d81d33ede98ebd291e1970e
@nb.njit(cache=True)
def lchToRGB(luma: float, chroma: float, hue: float) -> np.ndarray:
	hrad = hue * math.pi / 180.0
	a = math.cos(hrad) * chroma * 100
	b = math.sin(hrad) * chroma * 100

	CRE = 6.0 / 29.0

	y = (luma + 16) / 116.0
	x = y + a / 500.0
	z = y - b / 200.0

	x = 96422 * (x ** 3 if x > CRE else (116 * x - 16) / 903.3)
	y = 1.0 * (y ** 3 if luma > 8 else luma / 903.3)
	z = 0.82521 * (z ** 3 if z > CRE else (116 * z - 16) / 903.3)

	x =  0.9555766 * x - 0.0230393 * y + 0.0631636 * z
	y = -0.0282895 * x + 1.0099416 * y + 0.0210077 * z
	z =  0.0122982 * x - 0.0204830 * y + 1.3299098 * z

	r = 3.2404542 * x - 1.5371385 * y - 0.4985314 * z
	g = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z
	b = 0.0556434 * x - 0.2040259 * y + 1.0572252 * z

	r = 12.92 * r if r < 0.0031308 else 1.055 * math.pow(r, 1 / 2.4) - 0.055
	g = 12.92 * g if g < 0.0031308 else 1.055 * math.pow(g, 1 / 2.4) - 0.055
	b = 12.92 * b if b < 0.0031308 else 1.055 * math.pow(b, 1 / 2.4) - 0.055

	r = min(max(r, 0), 1)
	g = min(max(g, 0), 1)
	b = min(max(b, 0), 1)

	return np.asarray([r, g, b]).astype(np.float64).clip(0, 1)

@nb.njit(cache=True)
def simple3D(normal: complex, angle: float) -> float:
	h2 = 1.5    # height factor of the incoming light
	v = cmath.exp(complex(0,1) * angle * 2 * math.pi / 360)  # unit 2D vector in this direction
	normal /= abs(normal)  # normal vector: (u.re,u.im,1) 
	t = normal.real * v.real + normal.imag * v.imag + h2  # dot product with the incoming light

	return t / (1 + h2)   # rescale so that t does not get bigger than 1

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
@nb.njit(cache=True)
def phong3D(normal: complex, light: list[float]) -> float:
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

	Color palettes are numpy arrays of type flooat64 with shape (n,3).
	They contain at least 3 elements: first, last and default color.
	The default color is stored at the end of the array in element n-1.
	An array row contains the red, green and blue part of a color in range [0..1].
"""

#
# Create color palettes
#

def createLinearPalette(numColors: int, colorPoints: list = [(1., 1., 1.)], defColor: tuple = (0., 0., 0.)) -> np.ndarray:
	if len(colorPoints) == 0:
		# Greyscale palette
		palette = np.linspace((0., 0., 0.), (1., 1., 1.), max(numColors, 2), dtype=np.float64)
	elif (len(colorPoints) == 1):
		# Monochrome palette
		palette = np.full((max(numColors,1),3), colorPoints[0], dtype=np.float64)
	else:
		numColors = max(numColors,len(colorPoints))
		secSize = int(numColors/(len(colorPoints)-1))
		palette = np.array([colorPoints[0]], dtype=np.float64)
		for i in range(len(colorPoints)-1):
			if secSize + len(palette)-1 > numColors: secSize = numColors - len(palette)
			palette = np.vstack((palette[:-1], np.linspace(colorPoints[i], colorPoints[i+1], secSize, dtype=np.float64)))

	# Append default color and return palette
	return np.vstack((palette, np.array(defColor, dtype=np.float64)))
	
def createRGBPalette(numColors: int, startColor: tuple = (0., 0., 0.), endColor: tuple = (1., 1., 1.), defColor: tuple = (0., 0., 0.)) -> np.ndarray:
	return np.array([startColor, endColor, defColor], dtype=np.float64)

thetaList = [
	[.85, .0, .15],
	[.11, .02, .92],
	[.29, .02, 0.9],
	[.83, .01, .99],
	[.87, .83, .77],
	[.54, .38, .35],
	[.47, .51, .63],
	[.6, .57, .45],
	[.63, .83, .98],
	[.29, .52, .59]
]

def createSinusPalette(numColors: int, thetas: list = [.85, .0, .15], defColor: tuple = (0., 0., 0.)) -> np.ndarray:
	numColors = max(numColors, 2)
	ct = np.linspace(0, 1, numColors, dtype=np.float64)
	colors = np.column_stack(((
		ct + thetas[0]) * 2 * math.pi,
		(ct + thetas[1]) * 2 * math.pi,
		(ct + thetas[2]) * 2 * math.pi)
	)
	return np.vstack(((0.5 + 0.5 * np.sin(colors)), np.array(defColor, dtype=np.float64)))

def createSinusCosinusPalette(numColors: int, defColor: tuple = (0., 0., 0.)) -> np.ndarray:
	ct = np.arange(0, numColors, dtype=np.float64)
	colors = np.column_stack((
		ct/(numColors-1),
		(np.cos(ct * 0.1) + 1.0) * 0.5,
		(np.sin(ct * 0.01) + 1.0) * 0.5)
	)
	return np.vstack((colors, np.array(defColor, dtype=np.float64)))

