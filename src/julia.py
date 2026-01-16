
#
# Calculation of Julia set
#
#

import time
import math

import numpy as np
import numba as nb

import fractal as frc
import colors as col
import tkconfigure.tkconfigure as tkc

from constants import *

class Julia(frc.Fractal):

	def __init__(self, point: complex = complex(-0.7269, 0.1889), corner: complex = complex(-1.5, -1.5) , size: complex = complex(3.0, 3.0), maxIter: int = 500,
				stripes: int = 0, steps: int = 0, ncycle: int = 1):
		super().__init__(corner, size, stripes, steps, ncycle)

		self.settings.updateParameterDefinition({
			"Julia Set": {
				"point": {
					"inputtype": "complex",
					"initvalue": point,
					"widget":    "TKCEntry",
					"label":     "Point",
					"width":     20
				},
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

	def getParameterNames(self) -> list:
		return self.settings.getIds()

	def getMaxValue(self):
		maxIter, colorOptions, colorize = self.settings.getValues(['maxIter', 'colorOptions', 'colorize'])

		if colorOptions & FO_ORBITS: maxIter = max(maxIter, 1000)
		if colorize == FC_DISTANCE or colorize == FC_POTENTIAL: maxIter = max(maxIter, 4096)

		return maxIter

	def getCalcParameters(self) -> tuple:
		maxIter = self.getMaxValue()
		return super().getCalcParameters() + (self.settings['point'], maxIter)

# Iterate complex point using standard Mandelbrot formular Z = Z * Z + C
# Return color array [red, green, blue]
@nb.njit(cache=False)
def calculatePointZ2(Z, P, C, colorize, paletteMode, colorOptions, maxIter, bailout, colorPar, light):
	diaScale = maxIter/10.0

	dist = 0.0
	pot = 0.0
	stripe_a = 0.0
	stripe_s, stripe_sig, step_s, ncycle, diag = colorPar

	bStripe = stripe_s > 0
	bStep   = step_s > 0
	bOrbits = colorOptions & FO_ORBITS
	bDist   = colorize == FC_DISTANCE or bStripe or bStep

	nZ1 = 0.0               # Old value of abs(Z)^2
	D = complex(1.0, 0.0)   # 1st derivation
	period = 0              # Period counter for simplified orbit detection
	smooth_i = 0

	if bOrbits:
		orbits = np.zeros(maxIter, dtype=np.complex128)

	for i in range(0, maxIter+1):
		if bDist or colorOptions & FO_SHADING:
			D = D * 2 * Z

		Z = Z * Z + C

		if bStripe:
			stripe_t = (math.sin(stripe_s * math.atan2(Z.imag, Z.real)) + 1) / 2

		nZ = Z.real * Z.real + Z.imag * Z.imag
		if nZ > bailout:
			if bDist or bStripe:
				aZ = math.sqrt(nZ)
				log_ratio = 2*math.log(aZ) / math.log(bailout)
				smooth_i = 1 - math.log(log_ratio) / math.log(2)
				dist = aZ * math.log(aZ) / abs(D) / 2

			if bStripe:
				stripe_a = (stripe_a * (1 + smooth_i * (stripe_sig-1)) + stripe_t * smooth_i * (1 - stripe_sig))
				stripe_a = stripe_a / (1 - stripe_sig**i * (1 + smooth_i * (stripe_sig-1)))
			if colorize == FC_POTENTIAL:
				logZn = math.log(nZ)/2.0
				pot = math.log(logZn / math.log(2)) / math.log(2)	

			mapColorPar = [stripe_a, step_s, ncycle, float(maxIter), pot]

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

@nb.guvectorize([(nb.complex128[:], nb.float64[:,:], nb.int32, nb.int32, nb.int32, nb.float64[:], nb.float64[:], nb.complex128, nb.int32, nb.uint8[:,:])], '(n),(i,j),(),(),(),(k),(l),(),() -> (n,j)', nopython=True, cache=False, target='parallel')
def calculateVectorZ2(Z, P, colorize, paletteMode, colorOptions, colorPar, light, C, maxIter, R):
	bailout = 4.0 if colorize == FC_ITERATIONS and paletteMode != FP_HUE and colorOptions == 0 else 10**10

	for p in range(Z.shape[0]):
		R[p,:] = calculatePointZ2(Z[p], P, C, colorize, paletteMode, colorOptions, maxIter, bailout, colorPar, light)

