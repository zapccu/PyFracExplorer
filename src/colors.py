
import math
import cmath

import numpy as np
import numba as nb

from constants import *

"""
    ***************************************************************************
	 Predefined color tables
    ***************************************************************************
"""


colorTables = {
	"Monochrome": {
		"type": "Linear",
		"size": 4096,
		"par": [(1., 1., 1.)]
	},
	"Grey": {
		"type": "Linear",
		"size": 4096,
		"par": [(80/255, 80/255, 80/255), (1., 1., 1.)]
	},
	"Grey 256": {
		"type": "Linear",
		"size": 256,
		"par": [(80/255, 80/255, 80/255), (1., 1., 1.)]
	},
	"Blue - Grey - Blue": {
		"type": "Linear",
		"size": 4096,
		"par": [(.4, .4, .5), (.0, .0, 1.), (.4, .4, 128/255)]
	},
	"Sinus [.85, .0, .15]": {
		"type": "Sinus",
		"size": 4096,
		"par": [.85, .0, .15]
	},
	"Cosinus [0.1, 0, 2, 4]": {
		"type": "Cosinus",
		"size": 4096,
		"par": [0.1, 0, 2, 4]
	},
	"Sinus Cosinus": {
		"type": "SinusCosinus",
		"size": 4096,
		"par": [0.1, 0.01]
	},
	"Preset": {
		"type": "Sinus",
		"size": 4096,
		"par": [.85, .0, .15]
	}
}


###############################################################################
# Construct colors
#
# rgb is a numpy array of type float64 with elements [red, green, blue]
# rgbi is a numpy array of type uint8 with elements [red, green, blue]
###############################################################################

# Construct a rgb array. red, green, blue are in range 0..1
def rgb(red: float, green: float, blue: float) -> np.ndarray:
	return np.asarray([red, green, blue], dtype=np.float64)

# Construct a rgbi array. red, green, blue are in range 0..255
def rgbi(red: int, green: int, blue: int) -> np.ndarray:
	return np.asarray([red, green, blue], dtype=np.uint8)


###############################################################################
# RGB functions
###############################################################################

# Convert rgbi values to rgb values
def rgbf(red: int, green: int, blue: int) -> tuple[float, float, float]:
	return (red/255, green/255, blue/255)

# Convert rgb to rgbi
@nb.njit(cache=False)
def rgb2rgbi(rgb: np.ndarray) -> np.ndarray:
	return (rgb * 255).astype(np.uint8)

# Convert rgbi to rgb
def rgbi2rgb(rgbi: np.ndarray) -> np.ndarray:
	return (rgbi / 255).astype(np.float64)

# Convert rgbi to html color string
def rgbi2str(rgbi: np.ndarray) -> str:
	return '#{:02X}{:02X}{:02X}'.format(int(rgbi[0]), int(rgbi[1]), int(rgbi[2]))

# Convert html color string to rgbi
def str2rgbi(html: str) -> np.ndarray:
	if len(html) != 7:
		raise ValueError("Parameter html must be in format #rrggbb")
	return np.array([int(html[i:i+2], 16) for i in (1, 3, 5)], dtype=np.uint8)

# Convert html color string to rgbi
def str2rgb(html: str) -> np.ndarray:
	if len(html) != 7:
		raise ValueError("Parameter html must be in format #rrggbb")
	return np.array([int(html[i:i+2], 16) / 255 for i in (1, 3, 5)], dtype=np.float64)

# Convert integer value to rgb
def int2rgbi(intColor: int) -> np.ndarray:
	return np.asarray(((intColor >> 16) & 0xFF, (intColor >> 8) & 0xFF, intColor & 0xFF), dtype=np.uint8)

# Convert rgb value to integer value: 0xrrggbb
def rgbi2int(rgb: np.ndarray) -> int:
	return (int(rgb[2]) & 0xFF) | ((int(rgb[1]) & 0xFF) << 8) | ((int(rgb[0]) & 0xFF) << 16)


###############################################################################
# Color conversion functions
#
# Supported color spaces are rgb, xyz, lab, lch, oklch, hsl, hsb
###############################################################################

# Matrix-Vector multiplication to prevent installation of Scipy
@nb.njit(cache=False)
def mulDot(mat: np.ndarray, vec: np.ndarray) -> np.ndarray:
	r = np.zeros(vec.shape[0])
	for i in range(mat.shape[0]):
		for j in range(vec.shape[0]):
			r[i] = r[i] + mat[i,j] * vec[j]
	return r

# Convert rgb to xyz
@nb.njit(cache=False)
def rgb2xyz(rgb: np.ndarray) -> np.ndarray:
	a = np.where(rgb > 0.04045, ((rgb + 0.055) / 1.055) ** 2.4, rgb / 12.92)
	m = np.array([
		[0.4124, 0.3576, 0.1805],
        [0.2126, 0.7152, 0.0722],
        [0.0193, 0.1192, 0.9505]
	])
	# return np.dot(m, a)
	return mulDot(m, a)

# Convert xyz to rgb
@nb.njit(cache=False)
def xyz2rgb(xyz: np.ndarray) -> np.ndarray:	
	m = np.array([
		[ 3.24062548, -1.53720797, -0.4986286 ],
		[-0.96893071,  1.87575606,  0.04151752],
		[ 0.05571012, -0.20402105,  1.05699594]
	])
	# a = np.dot(m, xyz)
	a = mulDot(m, xyz)
	a[a < 0.] = 0.
	a = np.where(a > 0.0031308, 1.055 * np.power(a, 1. / 2.4) - 0.055, a * 12.92)
	a[a > 1.] = 1.
	return a

# Convert xyz to CIE lab (D65 white)
@nb.njit(cache=False)
def xyz2lab(xyz: np.ndarray) -> np.ndarray:
	D65_white = np.array([0.95047, 1., 1.08883])
	# D50_white = np.array([0.964212, 1., .825188])
	arr = xyz / D65_white
	arr = np.where(arr > 0.00885645, arr ** (1. / 3.), (7.78703704 * arr) + 16. / 116.)
	x, y, z = arr
	return np.array([(116. * y) - 16. , 500.0 * (x - y) , 200.0 * (y - z)], dtype=np.float64)

# Convert lab to xyz
@nb.njit(cache=False)
def lab2xyz(lab: np.ndarray):
	L, a, b = lab
	D65_white = np.array([0.95047, 1., 1.08883])
	# D50_white = np.array([0.964212, 1., .825188])
	y = (L + 16.) / 116.
	x = (a / 500.) + y
	z = y - (b / 200.)
	arr = np.array([x, y, z]) 
	arr = np.where(arr > 0.2068966, arr ** 3., (arr - 16. / 116.) / 7.78703704)
	return arr * D65_white

# Convert lab to lch
@nb.njit(cache=False)
def lab2lch(lab: np.ndarray) -> np.ndarray:
	L, a, b = lab
	h = np.arctan2(b, a)
	h = np.where(h > 0, h / np.pi * 180., 360. + h / np.pi * 180.)
	c = np.sqrt(a * a + b * b)
	return np.array([L, c, h], dtype=np.float64)

# Convert lab to oklch
@nb.njit(cache=False)
def lab2oklch(lab: np.ndarray) -> np.ndarray:
	l, a, b = lab
	h = math.atan2(b * a) * (180 / math.pi)
	if h < 0: h += 360
	c_max = 100                     # max chroma valua
	c = math.sqrt(a * a + b * b)
	c = (c / c_max) * 0.37          # chroma scaled to 0 .. 0.37
	l = math.round(((l + 16) / 116) * 1000) / 1000   # l in range 0 .. 1
	return np.array([l, c, h], dtype=np.float64)	

# Convert lch to lab
@nb.njit(cache=False)
def lch2lab(lch: np.ndarray) -> np.ndarray:
	l, c, h = lch
	a = math.cos(h * np.pi / 180.) * c
	b = math.sin(h * np.pi / 180.) * c
	return np.array([l, a, b ], dtype=np.float64)

# Convert oklch to lab
@nb.njit(cache=False)
def oklch2lab(oklch: np.ndarray) -> np.ndarray:
	l, c, h = oklch
	a = c * math.cos((h * math.pi) / 180)
	b = c * math.sin((h * math.pi) / 180)
	return np.array([l, a, b], dtype=np.float64)

# Convert rgb to lab
@nb.njit(cache=False)
def rgb2lab(rgb: np.ndarray) -> np.ndarray:
	return xyz2lab(rgb2xyz(rgb))

# Convert lab to rgb
@nb.njit(cache=False)
def lab2rgb(lab: np.ndarray) -> np.ndarray:
	return xyz2rgb(lab2xyz(lab))

# Convert rgb to lch
@nb.njit(cache=False)
def rgb2lch(rgb: np.ndarray) -> np.ndarray:
	return lab2lch(rgb2lab(rgb))

# Convert lch to rgb
@nb.njit(cache=False)
def lch2rgb(lch: np.ndarray) -> np.ndarray:
	return lab2rgb(lch2lab(lch))

# Convert hsl to rgb
@nb.njit(cache=False)
def hsl2rgb(hue: float, saturation: float, lightness: float) -> np.ndarray:
	if saturation == 0:
		return np.asarray([lightness, lightness, lightness])
	
	q = lightness * (1 + saturation) if lightness < 0.5 else lightness + saturation - lightness * saturation
	p = 2 * lightness - q

	r = _hueToRgb(p, q, hue + 1/3)
	g = _hueToRgb(p, q, hue)
	b = _hueToRgb(p, q, hue - 1/3)

	return np.asarray([r, g, b], dtype=np.float64)

@nb.njit(cache=False)
def _hueToRgb(p, q, t):
	if t < 0: t += 1
	if t > 1: t -= 1
	if t < 1/6: return p + (q - p) * 6 * t
	if t < 1/2: return q
	if t < 2/3: return p + (q - p) * (2/3 - t) * 6
	return p

# Convert hsb to rgb
@nb.njit(cache=False)
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


###############################################################################
# Shading functions (brightness calculation)
###############################################################################

###############################################################################
# Simple shading
#
# light: Light source for shading
#  0 = Angle in radians
#  1 = Angle elevation 0-90
#  8 = Height (1 + elevation[deg] / 90)
###############################################################################
@nb.njit(cache=False)
def simple3D(normal: complex, light: list[float]) -> float:
	# height factor of the incoming light
	# example for 45 deg elevation: 1 + 45/90 = 1.5
	# h2 = 1 + light[1]
	# => Stored in light[8]

	# unit 2D vector in this direction
	# r1 = exp(r)*cos(i), i1 = exp(r)*sin(i)
	# exp(complex(0,1)) * light[0]) == (cos(light[0], sin(light[0])))
	#v = cmath.exp(complex(0,1) * light[0])

	# normal /= abs(normal)
	absNormal = normal / abs(normal)
	vecNormal = [absNormal.real, absNormal.imag, 1.0]
	vecSimple = [math.cos(light[0]), math.sin(light[0]), 0.0]
	t = vecSimple[0] * vecNormal[0] +  vecSimple[1] * vecNormal[1] + vecSimple[2] * vecNormal[2] + light[8]

	# rescale so that t does not get bigger than 1
	bright = t / (1.0 + light[8])

	# Return brightness with optional offset
	return bright

###############################################################################
# Blinn Phong shading
#
# light: Light source for shading
#  0 = angle in radians
#  1 = elevation 0-90
#  2 = opacity 0-1
#  3 = ambiant 0-1
#  4 = diffuse 0-1
#  5 = spectral 0-1
#  6 = shininess 0-?
#  7 = gamma 0.1-10.0 (not used for shading)
###############################################################################
@nb.njit(cache=False)
def phong3D(normal: complex, light: list[float]) -> float:
	# Lambert normal shading (diffuse light)
	normal /= abs(normal)    

	# Diffuse light
	# theta:         light angle; phi: light azimuth
	# light vector:  [cos(theta)cos(phi), sin(theta)cos(phi), sin(phi)]
	# normal vector: [normal.real, normal.imag, 1]
	# ldiff:         diffuse light = dot product(light, normal)
	ldiff = (normal.real * math.cos(light[0]) * math.cos(light[1]) +
		normal.imag * math.sin(light[0]) * math.cos(light[1]) + 
		1 * math.sin(light[1]))
	# Normalization
	ldiff /= (1 + math.sin(light[1]))

	# Specular light
	# phi2:  average between phi and pi/2 (viewer azimuth)
	# lspec: specular light = dot product(phi2, normal)
	phi2 = (NC_PI12 + light[1]) / 2
	lspec = (normal.real * math.cos(light[0]) * math.sin(phi2) +
		normal.imag * math.sin(light[0]) * math.sin(phi2) +
		1 * math.cos(phi2))
	# Normalization
	lspec /= (1 + math.cos(phi2))

	# Shininess
	lspec = lspec ** light[6]

	# Brightness = ambiant + diffuse + specular
	bright = light[3] + light[4]*ldiff + light[5] * lspec

	# Add intensity
	bright = bright * light[2] + (1-light[2]) / 2

	# Return brightness with optional offset
	return bright



"""
    ***************************************************************************
	Color palettes

	Color palettes are numpy arrays of type float64 with shape (n,3).
	They contain at least 2 elements: first and last color.
	If a default color is specified it is stored at the end of the array.
	An array row contains red, green and blue parts of a color in range [0..1].
	***************************************************************************

"""

# Create a palette based on colorpoints with smooth transitions between colorpoints 
def createLinearPalette(numColors: int, colorPoints: list = [(1., 1., 1.)], defColor: tuple | None = None) -> np.ndarray:
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
	if defColor is None:
		return palette
	else:
		return np.vstack((palette, np.array(defColor, dtype=np.float64)))

def createRGBPalette(numColors: int, startColor: tuple = (0., 0., 0.), endColor: tuple = (1., 1., 1.), defColor: tuple | None = None) -> np.ndarray:
	if defColor is None:
		return np.array([startColor, endColor], dtype=np.float64)
	else:
		return np.array([startColor, endColor, defColor], dtype=np.float64)

# Create Sinus palette, depends on thetas
def createSinusPalette(numColors: int, thetas: list = [.85, .0, .15], defColor: tuple | None = None) -> np.ndarray:
	numColors = max(numColors, 2)
	ct = np.linspace(0, 1, numColors, dtype=np.float64)
	colors = np.column_stack((
		(ct + thetas[0]) * 2 * math.pi,
		(ct + thetas[1]) * 2 * math.pi,
		(ct + thetas[2]) * 2 * math.pi
	))
	if defColor is None:
		return 0.5 + 0.5 * np.sin(colors)
	else:
		return np.vstack(((0.5 + 0.5 * np.sin(colors)), np.array(defColor, dtype=np.float64)))

###############################################################################
# Create Cosine palette
#
# freq: frequency of the cosine wave [0,1]
# phase: list of phase shifts for r, g, b
###############################################################################
def createCosinePalette(numColors: int, freqphase: list = [0.1, 0, 2, 4], defColor: tuple | None = None) -> np.ndarray:
	freq = freqphase[0]
	phase = freqphase[1:]
	ct = np.arange(0, numColors, dtype=np.float64)
	colors = np.column_stack((
		0.5 * (1.0 + np.cos(ct * freq + phase[0])),
		0.5 * (1.0 + np.cos(ct * freq + phase[1])),
		0.5 * (1.0 + np.cos(ct * freq + phase[2]))
	))
	if defColor is None:
		return colors
	else:
		return np.vstack((colors, np.array(defColor, dtype=np.float64)))

# Create Sine/Cosine palette
def createSinusCosinusPalette(numColors: int, freq: list = [0.1, 0.01], defColor: tuple | None = None) -> np.ndarray:
	ct = np.arange(0, numColors, dtype=np.float64)
	colors = np.column_stack((
		ct/(numColors-1),
		(np.cos(ct * freq[0]) + 1.0) * 0.5,
		(np.sin(ct * freq[1]) + 1.0) * 0.5
	))
	if defColor is None:
		return colors
	else:
		return np.vstack((colors, np.array(defColor, dtype=np.float64)))

# Palette creation functions
paletteFunctions = {
	"Linear": createLinearPalette,
	"Sinus": createSinusPalette,
	"Cosinus": createCosinePalette,
	"SinusCosinus": createSinusCosinusPalette
}

# Create palette from dict
def createPaletteFromDef(paletteDef: dict, size: int = -1, defColor: tuple | None = None) -> np.ndarray:
	entries = size if size != -1 else paletteDef['size']
	fnc = paletteFunctions[paletteDef['type']]
	if 'par' not in paletteDef:
		return fnc(entries, defColor=defColor)
	else:
		return fnc(entries, paletteDef['par'], defColor=defColor)

# Create palette from colortable (list of rgb values)
def createPaletteFromList(colorTable: list, defColor: tuple | None = None) -> np.ndarray:
	if defColor is None:
		return np.array(colorTable, dtype=np.float64)
	else:
		return np.vstack((np.array(colorTable, dtype=np.float64), np.array(defColor, dtype=np.float64)))

# Create palette by name
def createPalette(name: str, size: int = -1, defColor: tuple | None = None) -> np.ndarray:
	return createPaletteFromDef(colorTables[name], size=size, defColor=defColor)
