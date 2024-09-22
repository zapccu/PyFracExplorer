
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

coords = [
	[-0.5503295086752807, -0.5503293049351449, -0.6259346555912755, -0.625934541001796],
	[-1.9854527029227764, -1.9854527027615938, 0.00019009159314173224, 0.00019009168379912058],
	[-1.749289287806423, -1.7492892878054118, -1.8709586016347623e-06, -1.8709580332005737e-06]
]

class Mandelbrot(frc.Fractal):

	def __init__(self, corner: complex = complex(-2.25, -1.5) , size: complex = complex(3.0, 3.0), maxIter: int = 500):
		super().__init__(size.real, size.imag, corner.real, corner.imag)

		self.settings.updateParameterDefinition({
			"Mandelbrot Set": {
				"maxIter": {
					"inputtype": "int",
					"valrange":  (10, 4000, 50),
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

# Iterate complex point using standard Mandelbrot formular Z = Z * Z + C
# Return rgbi color array [red, green, blue], dtype=uint8
# Values needed for color calculation:
@nb.njit(cache=True)
def calculatePointZ2(C, P, colorize, paletteMode, colorOptions, maxIter, light) -> np.ndarray:
	bailout = 4.0 if colorize == frc._C_ITERATIONS and paletteMode != frc._P_HUE and colorOptions == 0 else 10000.0

	diaScale = maxIter/10.0

	dist = -1.0
	pot = -1.0

	stripe_s = 2.0
	stripe_sig = 0.9
	stripe = colorOptions & frc._O_STRIPES and stripe_s > 0 and stripe_sig > 0
	stripe_a = 0.0

	D = complex(1.0)   # 1st derivation
	Z = C              # Shortcut for 1st iteration

	period = 0         # Period counter for simplified orbit detection
	nZ1 = 0.0          # Old value of abs(Z)^2
	pow = 1            # Power of 2 for potential calculation

	if colorOptions & frc._O_ORBITS:
		orbits = np.zeros(maxIter, dtype=np.complex128)
		orbits[0] = complex(0,0)
		oc = 1

	for i in range(1, maxIter+1):
		if stripe:
			stripe_t = (math.sin(stripe_s*math.atan2(Z.imag, Z.real)) + 1) / 2

		nZ = Z.real * Z.real + Z.imag * Z.imag
		if nZ > bailout:
			aZ = math.sqrt(nZ)
			if stripe:
				log_ratio = 2*math.log(aZ) / math.log(bailout)
				smooth_i = 1 - math.log(log_ratio) / math.log(2)
				stripe_a = stripe_a * stripe_sig + stripe_t * (1-stripe_sig)
				stripe_a = stripe_a / (1 - stripe_sig**i * (1 + smooth_i * (stripe_sig-1)))
			if colorize == frc._C_DISTANCE:
				dist = aZ * math.log(aZ) / abs(D) / 2
			elif colorize == frc._C_POTENTIAL:
				logZn = math.log(nZ)/2.0
				pot = math.log(logZn / math.log(2)) / math.log(2)		

			return frc.mapColorValue(P, i/maxIter, nZ, Z/D, dist, stripe_a, light, colorize, paletteMode, colorOptions)

		if colorOptions & frc._O_ORBITS:
			# Search for orbits (full periodicity check)
			idx = frc.findOrbit(orbits[:i], Z, 1e-15, 1e-11)
			if idx > -1:
				return col.rgb2rgbi(col.hsb2rgb(min(1.0,(i-idx)/maxIter*diaScale), 1.0, 1-i/maxIter))
			orbits[oc] = Z
			oc += 1
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

		if colorize == frc._C_DISTANCE or colorOptions & frc._O_SHADING:
			D = D * 2 * Z + 1

		Z = Z * Z + C

		if stripe:
			stripe_a = stripe_a * stripe_sig + stripe_t * (1-stripe_sig)

		pow *= 2

	return col.rgb2rgbi(P[-1])

@nb.guvectorize([(nb.complex128[:], nb.float64[:,:], nb.int32, nb.int32, nb.int32, nb.int32, nb.uint8[:,:])], '(n),(i,j),(),(),(),() -> (n,j)', nopython=True, cache=True, target='parallel')
def calculateVectorZ2(C, P, colorize, paletteMode, colorOptions, maxIter, R):
	if colorOptions & frc._O_ORBITS: maxIter = max(maxIter, 1000)

	# Light source for phong shading
	# 0 = Angle 0-360 degree
	# 1 = Angle elevation 0-90
	# 2 = opacity
	light = [45., 45., .75, .2, .5, .5, 20]
	light[0] = 2*math.pi*light[0]/360
	light[1] = math.pi/2*light[1]/90

	for p in range(C.shape[0]):
		R[p,:] = calculatePointZ2(C[p], P, colorize, paletteMode, colorOptions, maxIter, light)

