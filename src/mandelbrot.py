
#
# Calculation of Mandelbrot set
#
# References:
#
#   - Orbit detection: https://observablehq.com/@mcmcclur/orbit-detection-for-the-mandelbrot-set
#   - Blinn/Phong shading: https://github.com/jlesuffleur/gpu_mandelbrot/blob/master/mandelbrot.py
#

import time
import math

import numpy as np
import numba as nb

import fractal as frc
import colors as col
import tkconfigure as tkc


class Mandelbrot(frc.Fractal):

	def __init__(self, corner: complex = complex(-2.25, -1.5) , size: complex = complex(3.0, 3.0), maxIter: int = 500,
			  stripes: int = 0, steps: int = 0, ncycle: int = 1):
		super().__init__(size.real, size.imag, corner.real, corner.imag, stripes, steps, ncycle)

		# Add mandelbrot settings to fractal settings
		self.settings.updateParameterDefinition({
			"Mandelbrot Set": {
				"maxIter": {
					"inputtype": "int",
					"valrange":  (10, 5000, 50),
					"initvalue": maxIter,
					"widget":    "TKCSpinbox",
					"label":     "Max. iterations",
					"width":     6
				}
			}
		})

	# Called by beginCalc() before calculation is started
	def updateParameters(self):
		self.settings.syncConfig()
		corner = self.settings['corner']
		size   = self.settings['size']
		self.setDimensions(size.real, size.imag, corner.real, corner.imag)

	def getParameterNames(self) -> list:
		return self.settings.getIds()

	def getMaxValue(self):
		return 4096 if self.settings['colorize'] == frc._C_DISTANCE else self.settings['maxIter']

	def getCalcParameters(self) -> tuple:
		maxIter = self.getMaxValue()
		return super().getCalcParameters()+(maxIter,)

###############################################################################
#
# Iterate complex point using standard Mandelbrot formular Z = Z * Z + C
#
# Parameters:
#
#   C - Point in complex plain
#
#   P - Color palette np.array((n, 3), dtype=float64), rgb range = 0-1
#
#   colorize - Value to be used for color calculation:
#      _C_ITERATIONS - Number of iterations
#      _C_DISTANCE   - Distance to mandelbrot set
#      _C_POTENTIAL  - Potential
#
#   paletteMode - How to map calculation result to color palette:
#      _P_LINEAR - Linear mapping
#      _P_MODULO - Mapping by modulo division
#      _P_HUE - Mapping to HSB colorspace with hue = P[0,0], saturation P[0,1]
#      _P_HUEDYN - Mapping to HSB colorspace with calculated hue value
#      _P_LCHDYN - Mapping to LCH colorspace with calculated values
#
#   colorOptions - Combination of flags for modifying color calculation:
#      _F_ORBITS - Colorize orbits inside mandelbrot set
#      _F_STRIPES - Draw stripes
#      _F_SIMPLE_3D - Simple 3D shading (cannot be combined with _F_BLINNPHONG_3D)
#      _F_BLINNPHONG_3D - Blinn-Phong 3D shading (cannot be combinded with _F_SIMPLE_3D)
#
#   maxIter - Maximum number of iterations
#
#   bailout - Bailout radius
#
#   colorPar - Color calculation parameters:
#      [0] = stripe_s   - Stripe density, frequency for stripe average coloring
#                         Range 0-32, 0 = No stripes, default = 0
#      [1] = stripe_sig - Memory parameter for stripe average coloring
#                         Range 0-1, 0 = No stripes, default = 0.9
#      [2] = step_s     - Step density, frequency for step coloring
#                         Range 0-100, 0 = No steps, default = 0
#      [3] = ncycle     - Number of iteration before cycling the colortable
#                         Range 1-200, 1 = No cycling, default = 32
#
#   light - Light parameters for shading
#
# Return:
#
#   rgbi color array [red, green, blue], dtype=uint8, rgb range = 0-255
#
###############################################################################
@nb.njit(cache=True)
def calculatePointZ2(C: complex, P: np.ndarray, colorize: int, paletteMode: int, colorOptions: int, maxIter: int, bailout: float,
					 colorPar: list[float], light: list[float]) -> np.ndarray:
	diaScale = maxIter/10.0

	dist = -1.0
	pot = -1.0

	stripe_a   = 0.0
	stripe_s, stripe_sig, step_s, ncycle = colorPar
	bStripe = colorOptions & frc._O_STRIPES
	bStep   = colorOptions & frc._O_STEPS
	bOrbits = colorOptions & frc._O_ORBITS

	Z = 0
	nZ1 = 0.0          # Old value of abs(Z)^2
	D = complex(1.0)   # 1st derivation
	period = 0         # Period counter for simplified orbit detection

	if bOrbits:
		orbits = np.zeros(maxIter, dtype=np.complex128)

	for i in range(0, maxIter+1):
		if colorize == frc._C_DISTANCE or colorOptions & frc._O_SHADING:
			D = D * 2 * Z + 1

		Z = Z * Z + C

		if bStripe:
			stripe_t = (math.sin(stripe_s * math.atan2(Z.imag, Z.real)) + 1) / 2

		nZ = Z.real * Z.real + Z.imag * Z.imag
		if nZ > bailout:
			aZ = math.sqrt(nZ)
			if bStripe or bStep:
				log_ratio = 2*math.log(aZ) / math.log(bailout)
				smooth_i = 1 - math.log(log_ratio) / math.log(2)
				i += smooth_i

			if bStripe:
				stripe_a = stripe_a * stripe_sig + stripe_t * (1-stripe_sig)
				stripe_a = stripe_a / (1 - stripe_sig**i * (1 + smooth_i * (stripe_sig-1)))

			if colorize == frc._C_DISTANCE or bStripe:
				dist = aZ * math.log(aZ) / abs(D) / 2
			elif colorize == frc._C_POTENTIAL:
				logZn = math.log(nZ)/2.0
				pot = math.log(logZn / math.log(2)) / math.log(2)		

			return frc.mapColorValue(P, i/maxIter, nZ, Z/D, dist, [stripe_a, step_s, ncycle], light, colorize, paletteMode, colorOptions)

		if bOrbits:
			# Search for orbits (full periodicity check)
			idx = frc.findOrbit(orbits[:i], Z, 1e-15, 1e-11)
			if idx > -1:
				# Found orbit, colorize point inside mandelbrot set
				return col.rgb2rgbi(col.hsb2rgb(min(1.0,(i-idx)/maxIter*diaScale), 1.0, 1-i/maxIter))
			orbits[i] = Z
		else:
			# Simplified periodicity check, no orbit colorization
			if abs(nZ - nZ1) < 1e-10:
				i = maxIter
				break
			else:
				period += 1
				if period > 20:
					period = 0
					nZ1 = nZ

		if bStripe:
			stripe_a = stripe_a * stripe_sig + stripe_t * (1-stripe_sig)

	return col.rgb2rgbi(P[-1])

@nb.guvectorize([(nb.complex128[:], nb.float64[:,:], nb.int32, nb.int32, nb.int32, nb.int32, nb.uint8[:,:])], '(n),(i,j),(),(),(),() -> (n,j)', nopython=True, cache=True, target='parallel')
def calculateVectorZ2(C, P, colorize, paletteMode, colorOptions, maxIter, R):
	if colorOptions & frc._O_ORBITS: maxIter = max(maxIter, 1000)
	bailout = 4.0 if colorize == frc._C_ITERATIONS and paletteMode != frc._P_HUE and colorOptions == 0 else 10000.0

	# 0 = stripe_s
	# 1 = stripe_sig
	# 2 = step_s
	# 3 = ncycle
	colorPar = [2.0, 0.9, 0.0, 32.0]

	# Light source for phong shading
	# 0 = Angle 0-360 degree
	# 1 = Angle elevation 0-90
	# 2 = opacity 0-1
	# 3 = ambiant 0-1
	# 4 = diffuse 0-1
	# 5 = spectral 0-1
	# 6 = shininess 0-?
	light = [45., 45., .75, .2, .5, .5, 20]
	light[0] = 2*math.pi*light[0]/360
	light[1] = math.pi/2*light[1]/90

	for p in range(C.shape[0]):
		R[p,:] = calculatePointZ2(C[p], P, colorize, paletteMode, colorOptions, maxIter, bailout, colorPar, light)

