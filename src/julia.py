
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
import tkconfigure as tkc


class Julia(frc.Fractal):

	def __init__(self, point: complex = complex(-0.7269, 0.1889), corner: complex = complex(-1.5, -1.5) , size: complex = complex(3.0, 3.0), maxIter: int = 500):
		super().__init__(size.real, size.imag, corner.real, corner.imag)

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
		return super().getCalcParameters() + (self.settings['point'], maxIter)

# Iterate complex point using standard Mandelbrot formular Z = Z * Z + C
# Return color array [red, green, blue]
@nb.njit(cache=True)
def calculatePointZ2(Z, P, C, colorize, paletteMode, colorOptions, maxIter, light):
	bailout = 4.0 if colorize == frc._C_ITERATIONS and paletteMode != frc._P_HUE and colorOptions == 0 else 10000.0

	dst = 0.0      # Distance
	pot = 0.0      # Potential
	diaScale = maxIter/10.0

	stripe_s = 0.0
	stripe_sig = 0.9
	stripe = stripe_s > 0 and stripe_sig > 0
	stripe_a = 0.0

	D = complex(1.0)   # 1st derivation

	period = 0         # Period counter for simplified orbit detection
	nZ1 = 0.0          # Old value of abs(Z)^2
	pow = 1            # Power of 2 for potential calculation

	if colorOptions & frc._O_ORBITS:
		# Create array for periodicity check
		orbits = np.zeros(maxIter, dtype=np.complex128)
		orbits[0] = complex(0,0)
		oc = 1

	for i in range(1, maxIter+1):
		nZ = Z.real * Z.real + Z.imag * Z.imag
		if nZ > bailout: break

		if colorOptions & frc._O_STRIPES and stripe:
			stripe_t = (math.sin(stripe_s*math.atan2(Z.imag, Z.real)) + 1) / 2
			stripe_a = stripe_a * stripe_sig + stripe_t * (1-stripe_sig)

		if colorOptions & frc._O_ORBITS:
			# Search for orbits (full periodicity check)
			idx = frc.findOrbit(orbits[:i], Z, 1e-15, 1e-11)
			if idx > -1:
				return col.rgb2rgbi(col.hsb2rgb(min(1.0,(i-idx)/maxIter*diaScale), 1.0, 1-i/maxIter))
			orbits[oc] = Z
			oc += 1
		else:
			# Simplified periodicity check
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

		pow *= 2

	if i == maxIter:
		return col.rgb2rgbi(P[-1])
	
	if colorize == frc._C_DISTANCE:
		aZ = abs(Z)
		value = math.sqrt(aZ / abs(D)) * 0.5 * math.log(aZ)
		# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
		# distance = aZ / abs(distance) * 2.0 * log(aZ)
		# Convert to value between 0 and 1:
		# np.tanh(distance*resolution/size)
	elif colorize == frc._C_POTENTIAL:
		logZn = math.log(nZ)/2.0
		value = math.log(logZn / math.log(2)) / math.log(2)		
	else:
		value = float(i)

	if colorOptions & frc._O_SIMPLE_3D:
		shading = col.simple3D(Z/D, light[0])
	elif colorOptions & frc._O_BLINNPHONG_3D:
		shading = col.phong3D(Z/D, light)
	else:
		shading = 1.0

	return frc.mapColorValue(P, value, maxIter, shading, colorize, paletteMode)


@nb.guvectorize([(nb.complex128[:], nb.float64[:,:], nb.int32, nb.int32, nb.int32, nb.complex128, nb.int32, nb.uint8[:,:])], '(n),(i,j),(),(),(),(),() -> (n,j)', nopython=True, cache=True, target='parallel')
def calculateVectorZ2(Z, P, colorize, paletteMode, colorOptions, C, maxIter, R):
	if colorOptions & frc._O_ORBITS: maxIter = max(maxIter, 1000)

	# Light source for phong shading
	light = [45., 45., .75, .2, .5, .5, 20]
	light[0] = 2*math.pi*light[0]/360
	light[1] = math.pi/2*light[1]/90

	for p in range(Z.shape[0]):
		R[p,:] = calculatePointZ2(Z[p], P, C, colorize, paletteMode, colorOptions, maxIter, light)