
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
		super().__init__(corner, size, stripes, steps, ncycle)

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
		# Read parameters from widgets
		self.settings.syncConfig()

	def getParameterNames(self) -> list:
		return self.settings.getIds()

	def getMaxValue(self):
		maxIter      = self.settings['maxIter']
		colorOptions = self.settings['colorOptions']
		colorize     = self.settings['colorize']

		if colorOptions & frc._O_ORBITS: maxIter = max(maxIter, 1000)
		if colorize == frc._C_DISTANCE or colorize == frc._C_POTENTIAL: maxIter = max(maxIter, 4096)

		return maxIter

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
#      [4] = diag       - Distance normalization value
#
#   light - Light parameters for shading
#
# Return:
#
#   rgbi color array [red, green, blue], dtype=uint8, rgb range = 0-255
#
###############################################################################
@nb.njit(cache=False)
def calculatePointZ2(C: complex, P: np.ndarray, colorize: int, paletteMode: int, colorOptions: int, maxIter: int, bailout: float,
					 colorPar: list[float], light: list[float]) -> np.ndarray:
	diaScale = maxIter/10.0

	dist = 0.0
	pot = 0.0
	stripe_a = 0.0
	stripe_s, stripe_sig, step_s, ncycle, diag = colorPar

	bStripe = colorOptions & frc._O_STRIPES
	bStep   = colorOptions & frc._O_STEPS
	bOrbits = colorOptions & frc._O_ORBITS
	bDist   = colorize == frc._C_DISTANCE or bStripe or bStep

	Z = 0
	nZ1 = 0.0               # Old value of abs(Z)^2
	D = complex(1.0, 0.0)   # 1st derivation
	period = 0              # Period counter for simplified orbit detection

	if bOrbits:
		orbits = np.zeros(maxIter, dtype=np.complex128)

	for i in range(0, maxIter+1):
		if bDist:
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

			if bStripe:
				stripe_a = (stripe_a * (1 + smooth_i * (stripe_sig-1)) + stripe_t * smooth_i * (1 - stripe_sig))
				stripe_a = stripe_a / (1 - stripe_sig**i * (1 + smooth_i * (stripe_sig-1)))
			if bDist:
				dist = aZ * math.log(aZ) / abs(D) / 2
			elif colorize == frc._C_POTENTIAL:
				logZn = math.log(nZ)/2.0
				pot = math.log(logZn / math.log(2)) / math.log(2)	

			mapColorPar = [stripe_a, step_s, ncycle, float(maxIter)]

			return frc.mapColorValue(P, float(i+smooth_i), nZ, Z/D, dist/diag, mapColorPar, light, colorize, paletteMode, colorOptions)

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

@nb.guvectorize([(nb.complex128[:], nb.float64[:,:], nb.int32, nb.int32, nb.int32, nb.float64[:], nb.float64[:], nb.int32, nb.uint8[:,:])], '(n),(i,j),(),(),(),(k),(l),() -> (n,j)', nopython=True, cache=False, target='parallel')
def calculateVectorZ2(C, P, colorize, paletteMode, colorOptions, colorPar, light, maxIter, R):
	bailout = 4.0 if colorize == frc._C_ITERATIONS and paletteMode != frc._P_HUE and colorOptions == 0 else 10**10

	for p in range(C.shape[0]):
		R[p,:] = calculatePointZ2(C[p], P, colorize, paletteMode, colorOptions, maxIter, bailout, colorPar, light)

