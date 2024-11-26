
import time
import math

import numpy as np
import numba as nb
import tkconfigure.src.tkconfigure as tkc
import colors as col

from constants import *


#####################################################################
# Base class for all kind of Mandelbrot and Julia sets
#####################################################################

class Fractal:

	def __init__(self, corner: complex, size: complex, stripes: int = 0, steps: int = 0, ncycle: int = 1):

		"""
		Fractal light settings for shading, can be modified in separate dialog window.
		Internally stored as list with 8 elements:	

			0 = light angle 0-360 degree
			1 = elevation angle 0-90 degree
			2 = opacity 0-1, default=0.75, 0=dark
				Reduces the brightness
			3 = ambient light 0-1, default=0.2
				distant or indirect light. Objects are almost never completely dark. The ambient lighting constant simulates
				this and always gives the object some color
			4 = diffuse light 0-1, default=0.5
				Simulates the directional impact a light object has on an object. This is the most visually significant
				component of the lighting model. The more a part of an object faces the light source, the brighter it becomes.
			5 = specular light 0-1, default=0.5
				Simulates the bright spot of a light that appears on shiny objects. Specular highlights are more inclined to
				the color of the light than the color of the object.
			6 = shininess 1-30, default=20.0
			7 = gamma correction 0.1-10.0, default=1.0 (no correction)
		"""
		self.lightSettings = tkc.TKConfigure({
			"Light": {
				"angle": {
					"tooltip":   "Angle of light source",
					"inputtype": "float",
					"valrange":  (0, 360, 1),
					"initvalue": 45.0,
					"widget":    "TKCSlider",
					"label":     "Angle",
					"width":     120
				},
				"elevation": {
					"tooltip":   "Elevation angle",
					"inputtype": "float",
					"valrange":  (0, 90),
					"initvalue": 45.0,
					"widget":    "TKCSlider",
					"label":     "Elevation",
					"width":     120
				},
				"opacity": {
					"tooltip":   "Reduce the brightness, 0=dark",
					"inputtype": "float",
					"valrange":  (0.0, 1.0, 0.05),
					"initvalue": 0.75,
					"widget":    "TKCSlider",
					"label":     "Opacity",
					"width":     120
				},
				"ambient": {
					"tooltip":   """
Even when it is dark there is usually still some light somewhere in the world (the moon, a distant light)
so objects are almost never completely dark. The ambient lighting constant simulates this and always
gives the object some color""",
					"inputtype": "float",
					"valrange":  (0.0, 1.0, 0.1),
					"initvalue": 0.2,
					"widget":    "TKCSlider",
					"label":     "Ambient light",
					"width":     120
				},
				"diffuse": {
					"inputtype": "float",
					"valrange":  (0.0, 1.0, 0.1),
					"initvalue": 0.5,
					"widget":    "TKCSlider",
					"label":     "Diffuse light",
					"width":     120
				},
				"specular": {
					"inputtype": "float",
					"valrange":  (0.0, 1.0, 0.1),
					"initvalue": 0.5,
					"widget":    "TKCSlider",
					"label":     "Specular light",
					"width":     120
				},
				"shininess": {
					"inputtype": "float",
					"valrange":  (1.0, 30.0, 1.0),
					"initvalue": 20.0,
					"widget":    "TKCSlider",
					"label":     "Shininess",
					"width":     120
				},
				"gamma": {
					"tooltip":   "Gamma value for gamma correction. >1: lighten colors, <1: darken colors. Dark colors are more affected by this correction",
					"inputtype": "float",
					"valrange":  (0.1, 10.0, 0.1),
					"initvalue": 1.0,
					"widget":    "TKCSlider",
					"label":     "Gamma correction",
					"width":     120
				}
			}
		})

		# Fractal settings accessible in main window
		self.settings = tkc.TKConfigure({
			"Fractal": {
				"corner": {
					"tooltip":   "Complex corner of fractal",
					"inputtype": "complex",
					"initvalue": corner,
					"widget":    "TKCEntry",
					"label":     "Corner",
					"width":     25
				},
				"size": {
					"tooltip":   "Complex size of fractal",
					"inputtype": "complex",
					"initvalue": size,
					"widget":    "TKCEntry",
					"label":     "Size",
					"width":     25
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
					"valrange":  ["Orbits", "Inside distance", "Simple 3D", "Blinn/Phong 3D" ],
					"initvalue": 0,
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
					"width":     120
				},
				"steps": {
					"inputtype": "int",
					"valrange":  (0, 100),
					"initvalue": steps,
					"widget":    "TKCSlider",
					"label":     "Steps",
					"width":     120
				},
				"ncycle": {
					"inputtype": "int",
					"valrange":  (1, 200),
					"initvalue": ncycle,
					"widget":    "TKCSlider",
					"label":     "Cycles",
					"width":     120
				},
				"oversampling": {
					"inputtype": "int",
					"valrange":  (1, 3),
					"initvalue": 1,
					"widget":    "TKCSlider",
					"label":     "Oversampling",
					"width":     120
				}
			},
			"Light": {
				"light": {
					"inputtype": "tkc",
					"initvalue": self.lightSettings,
					"widget":    "TKCDialog",
					"label":     "Light",
					"width":     30,
					"readonly":  True,
					"widgetattr": {
						"width": 400,
						"height": 480,
						"padx":   10,
						"pady":   5
					}
				}
			}
		})

		# Calculation time measurement
		self.startTime = 0
		self.calcTime  = 0

	# Return tuple of calculation parameters depending on fractal type
	def getCalcParameters(self) -> tuple:

		"""
		colorPar: list with color related parameters:	

			0 = stripes
			1 = stripe_sig (0.9)
			2 = steps
			3 = sqrt(ncycle)
			4 = diag
		"""
		diag = abs(self.settings['size'])
		colorPar = [float(self.settings['stripes']), 0.9, float(self.settings['steps']), math.sqrt(self.settings['ncycle']), diag]

		"""		
		colorOptions: Flags for color mapping
		"""
		colorOptions = self.settings['colorOptions']
		if self.settings['stripes'] > 0 or self.settings['steps'] > 0:
			# Stripes and steps require 3D shading
			colorOptions = (colorOptions & FO_NOSHADING) | FO_BLINNPHONG_3D
			print("Added FO_BLINPHONG_3D to color options for stripes/steps support")
		print(f"Color options = {colorOptions}")

		"""
		light: Light source for shading		
		
			0 = Angle 0-360 degree
			1 = Angle elevation 0-90
			2 = opacity 0-1
			3 = ambiant 0-1
			4 = diffuse 0-1
			5 = specular 0-1
			6 = shininess 1-30
			7 = gamma correction 0.1-10.0
		"""
		light = self.settings['light'].getValues()
		print("Light = ", light)
		if colorOptions & FO_SIMPLE_3D:
			light[0] = light[0] * 2 * math.pi / 360
			light[1] = light[1] / 90
		else:
			light[0] = 2 * math.pi * light[0] / 360
			light[1] = math.pi / 2 * light[1] / 90

		return (self.settings['colorize'], self.settings['paletteMode'], colorOptions, colorPar, light)

	# Change fractal dimensions
	def setDimensions(self, corner: complex, size: complex, sync: bool = True):
		self.settings.setValues(sync=sync, corner=corner, size=size)

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
			self.settings.setValues(sync=True, corner=corner, size=size)

		return (corner, size)

	# Create matrix with mapping of screen coordinates to fractal coordinates
	def mapScreenCoordinates(self, imageWidth: int, imageHeight: int, aspectRatio: bool = True):
		corner, size = self.settings.getValues(['corner', 'size'])

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
		self.settings.syncConfig()
	
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
	l = O.shape[0]
	e = max(-1, l-100)
	for n in range(l, e, -1):
		d = Z - O[n]
		if d.real * d.real + d.imag * d.imag < tolerance1:
			break
	else:
		return -1
	
	for n in range(l, e, -1):
		d = Z - O[n]
		if d.real * d.real + d.imag * d.imag < tolerance2:
			return n
		
	return -1

# Map iteration result to color depending on mapping method
#
#   colorPar:
#     0 = stripe_a
#     1 = step_s
#     2 = ncycle
#     3 = maxIter
#
@nb.njit(cache=False)
def mapColorValue(palette: np.ndarray, iter: float, nZ: float, normal: complex, dist: float, colorPar: list[float],
				  light: list[float], colorize: int = 0, palettemode: int = 0, colorOptions: int = 0) -> np.ndarray:
	pLen = len(palette)-1
	stripe_a, step_s, ncycle, maxIter = colorPar

	if colorOptions & FO_SIMPLE_3D:
		bright = col.simple3D(normal, light)
	elif colorOptions & FO_BLINNPHONG_3D:
		bright = col.phong3D(normal, light)
	else:
		bright = 1.0

	if stripe_a > 0 or step_s > 0:
		color = shading(palette, iter, dist, colorPar, bright)
	elif colorize == FC_ITERATIONS:
		if palettemode == FP_LINEAR:
			color = palette[int(iter/maxIter * pLen)] * bright
		elif palettemode == FP_MODULO:
			color = palette[int(pLen * iter/maxIter) % int(ncycle)] * bright
		elif palettemode == FP_HUE:
			color = col.hsb2rgb(palette[0,0], palette[0,1], bright)
		elif palettemode == FP_HUEDYN:
			h = math.pow((iter) * 360, 1.5) % 360
			# For hsl model saturation must be set to 0.5
			color = col.hsb2rgb(h/360, 1.0, bright)
		elif palettemode == FP_LCHDYN:
			v = 1.0 - math.pow(math.cos(math.pi * iter), 2.0)
			# /100, /130
			color = col.lch2rgb(np.array([(75 - (75 * v)), (28 + (75 - (75 * v))), math.pow(360 * iter, 1.5) % 360])) * bright

	elif colorize == FC_DISTANCE:
		color = palette[int(math.tanh(dist) * pLen)] * bright

	elif colorize == FC_POTENTIAL:
		color = palette[int(pLen * iter/colorPar[3])] * bright

	# Gamma correction
	if light[7] != 1.0:
		return (np.pow(color, 1.0/light[7]) * 255).astype(np.uint8)
	else:
		return (color * 255).astype(np.uint8)

#
# Blending of 2 values (layers)
# Called by shading()
#
@nb.njit
def overlay(x: float, y: float, gamma: float):
	# https://en.wikipedia.org/wiki/Blend_modes#Overlay
	if (2*y) < 1:
		out = 2*x*y
	else:
		out = 1 - 2 * (1 - x) * (1 - y)
	return out * gamma + x * (1-gamma)

@nb.njit
def hardLight(x: float, y: float):
	return 2 * x * y if y < 0.5 else 1 - 2 * (1 - x) * (1 - y)

#
# Shading. Called for steps and stripes
#
@nb.njit
def shading(palette, niter, dist, colorPar, bright):
	stripe_a, step_s, ncycle, maxIter = colorPar
	pLen = len(palette)-2

	# Cycle through palette
	niter = math.sqrt(niter) % ncycle / ncycle
	palIdx = round(niter * pLen)

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
		light_step = hardLight(light_step2, light_step)
		nshader += 1
		shader += light_step

	# Applying shaders to brightness
	if nshader > 0:
		bright = hardLight(bright, shader/nshader) * (1-dist) + dist * bright

	color = np.copy(palette[palIdx])
	for i in range(3):
		color[i] = hardLight(color[i], bright)
	return color.clip(0, 1)
	
# Iterate a line from (x, y) to xy (horizontal or vertical, depending on 'orientation')
# orientation: 0 = horizontal, 1 = vertical
# Calculated line includes endpoint xy
# Returns colorline
def calculateSlices(C: np.ndarray, P: np.ndarray, iterFnc, calcParameters: tuple) -> np.ndarray:
	return iterFnc(C, P, *calcParameters)

def getUniqueColor(L: np.ndarray) -> np.ndarray:
	bUnique = 1 if np.all(L == L[0,:]) else 0
	return np.append(L[0], bUnique)

