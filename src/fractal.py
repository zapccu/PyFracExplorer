
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
_O_SHADING       = 12     # Mask for shading


#####################################################################
# Base class for all kind of Mandelbrot and Julia sets
#####################################################################

class Fractal:

	def __init__(self, fractalWidth: float, fractalHeight: float, offsetX: float = 0.0, offsetY: float = 0.0):
		self.settings = tkc.TKConfigure({
			"Fractal": {
				"corner": {
					"inputtype": "complex",
					"initvalue": complex(offsetX, offsetY),
					"widget":    "TKCEntry",
					"label":     "Corner",
					"width":     20
				},
				"size": {
					"inputtype": "complex",
					"initvalue": complex(fractalWidth, fractalHeight),
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
					"valrange":  ["Orbits", "Stripes", "Simple 3D", "Blinn/Phong 3D" ],
					"initvalue": 0,
					"widget":     "TKCFlags",
					"widgetattr": {
						"text": "Colorization options"
					},
					"row": 0,
					"column": 1
				}
			}
		})

		self.fractalWidth  = fractalWidth
		self.fractalHeight = fractalHeight
		self.offsetX       = offsetX
		self.offsetY       = offsetY

		self.startTime = 0
		self.calcTime  = 0
	
	# Return list of calculation parameters depending on fractal type
	def getCalcParameters(self) -> tuple:
		return (self.settings['colorize'], self.settings['paletteMode'], self.settings['colorOptions'])

	# Change fractal dimensions
	def setDimensions(self, fractalWidth: float, fractalHeight: float, offsetX: float = 0.0, offsetY: float = 0.0):
		self.fractalWidth  = fractalWidth
		self.fractalHeight = fractalHeight
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.settings.set('corner', complex(offsetX, offsetY), sync=True)
		self.settings.set('size', complex(fractalWidth, fractalHeight), sync=True)

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

		size = self.mapWH(w, h, imageWidth, imageHeight)
		corner = self.mapXY(x1, y1, imageWidth, imageHeight)
		self.setDimensions(size.real, size.imag, corner.real, corner.imag)

	# Pixel distance
	def dx(self, imageWidth: int) -> float:
		return self.fractalWidth / (imageWidth - 1)
	def dy(self, imageHeight: int) -> float:
		return self.fractalHeight / (imageHeight - 1)

	# Map screen coordinates to fractal coordinates
	def mapX(self, x: int, imageWidth: int) -> float:
		return self.offsetX + x * self.dx(imageWidth)
	def mapY(self, y: int, imageHeight: int) -> float:
		return self.offsetY + y * self.dy(imageHeight)
	def mapXY(self, x: int, y: int, imageWidth: int, imageHeight: int) -> complex:
		return complex(self.mapX(x, imageWidth), self.mapY(y, imageHeight))
	def mapWH(self, width: int, height: int, imageWidth: int, imageHeight: int) -> complex:
		return complex(self.dx(imageWidth) * width, self.dy(imageHeight) * height)
	
	# Create matrix with mapping of screen coordinates to fractal coordinates
	def mapScreenCoordinates(self, imageWidth: int, imageHeight: int):
		dxTab = np.outer(np.ones((imageWidth,), dtype=np.float64),
				   np.linspace(self.offsetX, self.offsetX+self.fractalWidth, imageWidth, dtype=np.float64))
		dyTab = np.outer(1j * np.linspace(self.offsetY, self.offsetY + self.fractalHeight, imageHeight, dtype=np.float64),
				   np.ones((imageHeight,), dtype=np.complex128))
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
@nb.njit(cache=True)
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
@nb.njit(cache=True)
def mapColorValue(palette: np.ndarray, value: float, maxValue: int, shading: float = 1.0, colorize: int = 0, palettemode: int = 0) -> np.ndarray:
	pLen = len(palette)-1
	color = palette[pLen]

	if colorize == _C_ITERATIONS:
		# value = iteration count
		if value == maxValue: return color
		if palettemode == _P_LINEAR:
			color = palette[int(value)] if maxValue == pLen else palette[int(pLen / maxValue * value)]
		elif palettemode == _P_MODULO:
			color = palette[int(value)] if maxValue == pLen else palette[int(value) % pLen]
		elif palettemode == _P_HUE:
			return col.hsbToRGB(palette[0,0], palette[0,1], shading)
		elif palettemode == _P_HUEDYN:
			h = math.pow((value/maxValue) * 360, 1.5) % 360
			# For hsl model saturation must be set to 0.5
			return col.hsbToRGB(h/360, 1.0, shading)
		elif palettemode == _P_LCHDYN:
			s = value/maxValue
			v = 1.0 - math.pow(math.cos(math.pi * s), 2.0)
			return col.lchToRGB((75 - (75 * v))/100, (28 + (75 - (75 * v)))/130, math.pow(360 * s, 1.5) % 360)
		
	elif colorize == _C_DISTANCE:
		# value = distance
		if value <= 0: return color
		color = palette[int(value * pLen)]

	elif colorize == _C_POTENTIAL:
		# value = potential
		if value <= 0: return color
		color = palette[int(value * pLen)]

	return (color * shading).astype(np.uint8)

	
# Iterate a line from (x, y) to xy (horizontal or vertical, depending on 'orientation')
# orientation: 0 = horizontal, 1 = vertical
# Calculated line includes endpoint xy
# Returns colorline
def calculateSlices(C: np.ndarray, P: np.ndarray, iterFnc, calcParameters: tuple) -> np.ndarray:
	return iterFnc(C, P, *calcParameters)

def getUniqueColor(L: np.ndarray) -> np.ndarray:
	bUnique = 1 if np.all(L == L[0,:]) else 0
	return np.append(L[0], bUnique)

