
import time
import math

import numpy as np
import numba as nb
import tkconfigure as tkc
import colors as col


#####################################################################
# Calculation and color mapping constants
#####################################################################

# Colorization modes
_C_ITERATIONS = 0         # Colorize by iterations
_C_DISTANCE   = 1         # Colorize by distance to mandelbrot set
_C_POTENTIAL  = 2         # Colorize by potential

# Color palette modes
_P_LINEAR = 0             # Linear color mapping to selected rgb palette
_P_MODULO = 1             # Color mapping by modulo division to selected rgb palette
_P_HUE    = 2             # Color mapping to hsv/hsl color space based on 1st palette entry
_P_HUEDYN = 3             # Color mapping to hsv/hsl color space, hue based on iterations
_P_LCHDYN = 4

# Colorization options
_O_ORBITS        = 1      # Draw orbits
_O_STRIPES       = 2      # Draw stripes
_O_SIMPLE_3D     = 4      # Colorize by distance with 3D shading
_O_BLINNPHONG_3D = 8      # Blinn/Phong 3D shading
_O_STEPS         = 16     # Steps

_O_SHADING       = 12     # Combination of _O_BLINNPHONG_3D, _O_SIMPLE_3D


###############################################################################
# Fractal presets
#
# Some taken from https://github.com/jlesuffleur/gpu_mandelbrot/tree/master
###############################################################################

presets = {
	'crown': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-0.5503295086752807, -0.5503293049351449, -0.6259346555912755, -0.625934541001796],
		'stripes':    2,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_STRIPES | _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.11, .02, .92]
			}
		}
	},
	'pow': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.9854527029227764, -1.9854527027615938, 0.00019009159314173224, 0.00019009168379912058],
		'stripes':    0,
		'steps':      10,
		'ncycle':     8,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_STEPS | _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.29, .02, 0.9]
			}
		}
	},
	'octogone': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.749289287806423, -1.7492892878054118, -1.8709586016347623e-06, -1.8709580332005737e-06],
		'stripes':    5,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_STRIPES | _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.83, .01, .99]
			}
		}
	},
	'julia': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.9415524417847085, -1.9415524394561112, 0.00013385928801614168, 0.00013386059768851223],
		'stripes':    0,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_STRIPES | _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.87, .83, .77]
			}
		}
	},
	'lightning': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-0.19569582393630502, -0.19569331188751315, 1.1000276413181806, 1.10002905416902],
		'stripes':    8,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_STRIPES | _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.54, .38, .35]
			}
		}
	},
	'web': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.7497082019887222, -1.749708201971718, -1.3693697170765535e-07, -1.369274301311596e-07],
		'stripes':    0,
		'steps':      20,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_STEPS | _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.47, .51, .63]
			}
		}
	},
	'wave': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.8605721473418524, -1.860572147340747, -3.1800170324714687e-06, -3.180016406837821e-06],
		'stripes':    12,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_STRIPES | _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.6, .57, .45]
			}
		}
	},
	'tiles': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-0.7545217835886875, -0.7544770820676441, 0.05716740181493137, 0.05719254327783547],
		'stripes':    2,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_STRIPES | _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.63, .83, .98]
			}
		}
	},
	'velvet': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.6241199193994318, -1.624119919281773, -0.00013088931048083944, -0.0001308892443058033],
		'stripes':    5,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_STRIPES | _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.29, .52, .59]
			}
		}
	},
	"color-vortex": {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'corner':     -0.6656224884756315+0.3546631894271655j,
		'size':       0.0018369561502944544+0.0018369561502944544j,
		'stripes':    4,
		'steps':      0,
		'ncycle':     19,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_STRIPES | _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.85, .0, .15]
			}
		}
	},
	"blue-julia": {
		'type':       'Julia',
		'maxIter':    2000,
		'corner':     -1.5-1.5j,
		'size':       3+3j,
		'point':      -0.7269+0.1889j,
		'stripes':    0,
		'steps':      0,
		'ncycle':     1,
		'colorize':   _C_ITERATIONS,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.85, .0, .15]
			}
		}
	}
}


#####################################################################
# Base class for all kind of Mandelbrot and Julia sets
#####################################################################

class Fractal:

	def __init__(self, corner: complex, size: complex, stripes: int = 0, steps: int = 0, ncycle: int = 1):

		colorOptions = 0
		if stripes > 0: colorOptions |= _O_STRIPES
		if steps > 0:   colorOptions |= _O_STEPS

		self.settings = tkc.TKConfigure({
			"Fractal": {
				"corner": {
					"inputtype": "complex",
					"initvalue": corner,
					"widget":    "TKCEntry",
					"label":     "Corner",
					"width":     20
				},
				"size": {
					"inputtype": "complex",
					"initvalue": size,
					"widget":    "TKCEntry",
					"label":     "Size",
					"width":     20
				}
			},
			"Colorization": {
				"colorize": {
					"inputtype": "int",
					"valrange":  ["Iterations", "Distance", "Potential"],
					"initvalue": 0,
					"widget":    "TKCRadiobuttons",
					"widgetattr": {
						"text": "Colorization mode"
					}
				},
				"paletteMode": {
					"inputtype": "int",
					"valrange":  ["Linear", "Modulo", "Hue", "Hue dynamic", "Luma Chroma Hue"],
					"initvalue": 0,
					"widget":     "TKCRadiobuttons",
					"widgetattr": {
						"text": "Color palette mode"
					}
				},
				"colorOptions": {
					"inputtype": "bits",
					"valrange":  ["Orbits", "Stripes", "Simple 3D", "Blinn/Phong 3D", "Steps" ],
					"initvalue": colorOptions,
					"widget":     "TKCFlags",
					"widgetattr": {
						"text": "Colorization options"
					}
				}
			},
			"Color Parameters": {
				"stripes": {
					"inputtype": "int",
					"valrange":  (0, 32),
					"initvalue": stripes,
					"widget":    "TKCSlider",
					"label":     "Stripes",
					"width":     12
				},
				"steps": {
					"inputtype": "int",
					"valrange":  (0, 100),
					"initvalue": steps,
					"widget":    "TKCSlider",
					"label":     "Steps",
					"width":     12
				},
				"ncycle": {
					"inputtype": "int",
					"valrange":  (1, 200),
					"initvalue": ncycle,
					"widget":    "TKCSlider",
					"label":     "Cycles",
					"width":     12
				},
				"oversampling": {
					"inputtype": "int",
					"valrange":  (1, 3),
					"initvalue": 1,
					"widget":    "TKCSlider",
					"label":     "Oversampling",
					"width":     12
				}
			},
			"Light": {
				"angle": {
					"inputtype": "float",
					"valrange":  (0, 360),
					"initvalue": 45.0,
					"widget":    "TKCSlider",
					"label":     "Angle",
					"width":     12
				},
				"elevation": {
					"inputtype": "float",
					"valrange":  (0, 90),
					"initvalue": 45.0,
					"widget":    "TKCSlider",
					"label":     "Elevation",
					"width":     12
				}
			}
		})

		self.startTime = 0
		self.calcTime  = 0

	# Return list of calculation parameters depending on fractal type
	def getCalcParameters(self) -> tuple:
		# Color related parameters
		#  0 = stripes
		#  1 = stripe_sig (0.9)
		#  2 = steps
		#  3 = sqrt(ncycle)
		#  4 = diag
		diag = abs(self.settings['size'])
		colorPar = [float(self.settings['stripes']), 0.9, float(self.settings['steps']), math.sqrt(self.settings['ncycle']), diag]

		# Light source for shading
		#  0 = Angle 0-360 degree
		#  1 = Angle elevation 0-90
		#  2 = opacity 0-1
		#  3 = ambiant 0-1
		#  4 = diffuse 0-1
		#  5 = spectral 0-1
		#  6 = shininess 0-?
		light = [self.settings['angle'], self.settings['elevation'], .75, .2, .5, .5, 20.]
		light[0] = 2 * math.pi * light[0] / 360
		light[1] = math.pi / 2 * light[1] / 90

		return (self.settings['colorize'], self.settings['paletteMode'], self.settings['colorOptions'], colorPar, light)

	# Change fractal dimensions
	def setDimensions(self, corner: complex, size: complex, sync: bool = True):
		self.settings.set('corner', corner, sync=sync)
		self.settings.set('size', size, sync=sync)

	# Change fractal coordinates
	def setCoordinates(self, left: float, right: float, bottom: float, top: float, sync: bool = True):
		self.setDimensions(complex(left, bottom), complex(right-left, top-bottom), sync=sync)

	# Zoom into screen area
	def zoomArea(self, imageWidth: int, imageHeight: int, x1: int, y1: int, x2: int, y2: int):
		size = self.mapWH(x2-x1+1, y2-y1+1, imageWidth, imageHeight)
		corner = self.mapXY(x1, y1, imageWidth, imageHeight)
		self.setDimensions(size.real, size.imag, corner.real, corner.imag)

	# Zoom in or out by specified percentage value
	def zoom(self, percent: float, imageWidth: int, imageHeight: int, x: int = 0, y: int = 0):
		if percent == 100 or percent < 1: return

		w = int(imageWidth * 1 / percent * 100)
		h = int(imageHeight * 1 / percent * 100)

		x1 = int(x - w / 2) if x > 0 else int((imageWidth - w) / 2)
		y1 = int(y - h / 2) if y > 0 else int((imageHeight - h) / 2)

		size   = self.mapWH(w, h, imageWidth, imageHeight)
		corner = self.mapXY(x1, y1, imageWidth, imageHeight)
		self.setDimensions(corner, size)

	# Pixel distance
	def dx(self, imageWidth: int) -> float:
		size = self.settings['size']
		return size.real / (imageWidth - 1)
	def dy(self, imageHeight: int) -> float:
		size = self.settings['size']
		return size.imag / (imageHeight - 1)

	# Map screen coordinates to fractal coordinates
	def mapX(self, x: int, imageWidth: int) -> float:
		corner = self.settings['corner']
		return corner.real + x * self.dx(imageWidth)
	def mapY(self, y: int, imageHeight: int) -> float:
		corner = self.settings['corner']
		return corner.imag + y * self.dy(imageHeight)
	def mapXY(self, x: int, y: int, imageWidth: int, imageHeight: int) -> complex:
		return complex(self.mapX(x, imageWidth), self.mapY(y, imageHeight))
	def mapWH(self, width: int, height: int, imageWidth: int, imageHeight: int) -> complex:
		return complex(self.dx(imageWidth) * width, self.dy(imageHeight) * height)
	
	# Adjust fractal aspect ratio to image aspect ratio
	def adjustAspectRatio(self, imageWidth: int, imageHeight: int, corner: complex, size: complex) -> tuple[complex]:
		imageRatio = imageWidth/imageHeight
		fractalRatio = size.real / size.imag

		if imageRatio != fractalRatio:
			fractalHeight = size.real / imageRatio
			corner = complex(corner.real, corner.imag + (size.imag - fractalHeight) / 2)
			size   = complex(size.real, fractalHeight)
			self.settings.set('corner', corner, sync=True)
			self.settings.set('size', size, sync=True)

		return (corner, size)

	# Create matrix with mapping of screen coordinates to fractal coordinates
	def mapScreenCoordinates(self, imageWidth: int, imageHeight: int, aspectRatio: bool = True):
		corner = self.settings['corner']
		size = self.settings['size']

		if aspectRatio:
			corner, size = self.adjustAspectRatio(imageWidth, imageHeight, corner, size)

		dxTab = np.outer(np.ones((imageHeight,), dtype=np.float64),
				   np.linspace(corner.real, corner.real + size.real, imageWidth, dtype=np.float64))
		dyTab = np.outer(1j * np.linspace(corner.imag, corner.imag + size.imag, imageHeight, dtype=np.float64),
				   np.ones((imageWidth,), dtype=np.complex128))
		self.cplxGrid = dxTab + dyTab

	# Maximum calculation value (i.e. max iterations)
	def getMaxValue(self):
		return 1
	
	def updateParameters(self):
		pass
	
	# Called before calculation is started
	def beginCalc(self, screenWidth: int, screenHeight: int) -> bool:
		self.updateParameters()
		self.mapScreenCoordinates(screenWidth, screenHeight)
		self.startTime = time.time()
		return True

	# Called after calculation is finished
	def endCalc(self) -> float:
		self.endTime = time.time()
		self.calcTime = self.endTime-self.startTime+1
		return self.calcTime


# Find orbit
@nb.njit(cache=False)
def findOrbit(O: np.ndarray, Z: complex, tolerance1: float, tolerance2: float):
	for n in range(O.shape[0], -1, -1):
		d = Z - O[n]
		if d.real * d.real + d.imag * d.imag < tolerance1:
			break
	else:
		return -1
	
	for n in range(O.shape[0], -1, -1):
		d = Z - O[n]
		if d.real * d.real + d.imag * d.imag < tolerance2:
			return n
		
	return -1

# Map iteration result to color depending on mapping method
#
#   colorPar
#     0 = stripe_a
#     1 = step_s
#     2 = ncycle
#     3 = maxIter
#
@nb.njit(cache=False)
def mapColorValue(palette: np.ndarray, iter: float, nZ: float, normal: complex, dist: float, colorPar: list[float],
				  light: list[float], colorize: int = 0, palettemode: int = 0, colorOptions: int = 0) -> np.ndarray:
	pLen = len(palette)-1

	if colorOptions & _O_SIMPLE_3D:
		bright = col.simple3D(normal, light[0], light[1])
	elif colorOptions & _O_BLINNPHONG_3D:
		bright = col.phong3D(normal, light)
	else:
		bright = 1.0

	if colorOptions & _O_STRIPES or colorOptions & _O_STEPS:
		color = shading(palette, iter, dist, normal, colorPar, bright)
	elif colorize == _C_ITERATIONS:
		if palettemode == _P_LINEAR:
			color = palette[int(iter/colorPar[3] * pLen)] * bright
		elif palettemode == _P_MODULO:
			color = palette[int(pLen * iter/colorPar[3]) % int(colorPar[2])] * bright
		elif palettemode == _P_HUE:
			color = col.hsb2rgb(palette[0,0], palette[0,1], bright)
		elif palettemode == _P_HUEDYN:
			h = math.pow((iter) * 360, 1.5) % 360
			# For hsl model saturation must be set to 0.5
			color = col.hsb2rgb(h/360, 1.0, bright)
		elif palettemode == _P_LCHDYN:
			v = 1.0 - math.pow(math.cos(math.pi * iter), 2.0)
			color = col.lchToRGB((75 - (75 * v))/100, (28 + (75 - (75 * v)))/130, math.pow(360 * iter, 1.5) % 360) * bright
		
	elif colorize == _C_DISTANCE:
		color = palette[int(math.tanh(dist) * pLen)] * bright

	elif colorize == _C_POTENTIAL:
		color = palette[int(pLen * iter/colorPar[3])] * bright

	return (color * 255).astype(np.uint8)
	# return col.rgb2rgbi(color * bright)

@nb.njit
def overlay(x, y, gamma):
	if (2*y) < 1:
		out = 2*x*y
	else:
		out = 1 - 2 * (1 - x) * (1 - y)
	return out * gamma + x * (1-gamma)

@nb.njit
def shading(palette, niter, dist, normal, colorPar, bright):
	stripe_a, step_s, ncycle, maxIter = colorPar
	pLen = len(palette)-2

    # Cycle through palette
	niter = math.sqrt(niter) % ncycle / ncycle
	palIdx = round(niter * pLen)

	# overlay = lambda x, y, gamma: (2 * x * y if 2 * y < 1 else 1 - 2 * (1 - x) * (1 - y)) * gamma + x * (1 - gamma)
    
    # distance estimation: log transform and sigmoid on [0,1] => [0,1]
	dist = -math.log(dist) / 12
	dist = 1 / (1 + math.exp(-10 * ((2 * dist - 1)/2)))

    # Shaders: steps and/or stripes
	nshader = 0
	shader = 0

    # Stripe shading
	if stripe_a > 0:
		nshader += 1
		shader += stripe_a

    # Step shading
	if step_s > 0:
		# Color update: constant color on each major step
		step_s = 1/step_s                                 
		palIdx = round((niter - niter % step_s) * pLen)

		# Major step: step_s frequency
		x = niter % step_s / step_s
		light_step = 6 * (1 - x**5 - (1 - x)**100) / 10

		# Minor step: n for each major step
		step_s = step_s/8
		x = niter % step_s / step_s
		light_step2 = 6 * (1 - x**5 - (1 - x)**30) / 10

		# Overlay merge between major and minor steps
		light_step = overlay(light_step2, light_step, 1)
		nshader += 1
		shader += light_step

    # Applying shaders to brightness
	if nshader > 0:
		bright = overlay(bright, shader/nshader, 1) * (1-dist) + dist * bright

	# color = overlay(palette[palIdx], bright, 1)
	color = np.zeros(3, dtype=np.float64)
	for i in range(3):
		color[i] = palette[palIdx,i]
		color[i] = overlay(color[i], bright, 1)
		color[i] = max(0,min(1, color[i]))
	return color

	# return color.clip(0, 1)
	
# Iterate a line from (x, y) to xy (horizontal or vertical, depending on 'orientation')
# orientation: 0 = horizontal, 1 = vertical
# Calculated line includes endpoint xy
# Returns colorline
def calculateSlices(C: np.ndarray, P: np.ndarray, iterFnc, calcParameters: tuple) -> np.ndarray:
	return iterFnc(C, P, *calcParameters)

def getUniqueColor(L: np.ndarray) -> np.ndarray:
	bUnique = 1 if np.all(L == L[0,:]) else 0
	return np.append(L[0], bUnique)

