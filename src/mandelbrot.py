
import time

import numpy as np
import numba as nb

from math import *

import fractal as frc
import colors as col
import tkconfigure as tkc


# Flags
_F_POTENTIAL  = 1   # Calculate potential
_F_DISTANCE   = 2   # Calculate distance
_F_ORBITCOLOR = 4   # Colorize orbits


class Mandelbrot(frc.Fractal):

	_resultNames    = ( 'maxIter', 'iterations', 'Z', 'distance' )

	def __init__(self, corner: complex = complex(-2.25, -1.5) , size: complex = complex(3.0, 3.0), maxIter: int = 256):
		super().__init__(size.real, size.imag, corner.real, corner.imag)

		self.settings.setParameterDefinition({
			"Mandelbrot Set": {
				"corner": {
					"inputtype": "complex",
					"initvalue": corner,
					"widget":    "TKCEntry",
					"label":     "Corner",
					"width":     10
				},
				"size": {
					"inputtype": "complex",
					"initvalue": size,
					"widget":    "TKCEntry",
					"label":     "Size",
					"width":     10
				},
				"maxIter": {
					"inputtype": "int",
					"valrange":  (10, 4000, 50),
					"initvalue": maxIter,
					"widget":    "TKCSpinbox",
					"label":     "Max. iterations",
					"width":     6
				},
				"maxDiameter": {
					"inputtype": "int",
					"valrange":  (0, 10),
					"initvalue": 10,
					"widget":    "TKCSpinbox",
					"label":     "Max. diameter",
					"width":     6
				},
				"flags": {
					"inputtype": "bits",
					"valrange":  ["Potential", "Distance"],
					"initvalue": 0,
					"widget":     "TKCFlags",
					"widgetattr": {
						"text": "Calculation options"
					}
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
		return 4096 if self.settings['flags'] & _F_DISTANCE else self.settings['maxIter']

	def getCalcParameters(self) -> tuple:
		maxIter = self.getMaxValue()
		return (self.settings['flags'], maxIter, self.settings['maxDiameter'])
	
# Iterate complex point
# Return tuple with results
@nb.njit(cache=True)
def calculatePointZ2(C, P, flags, maxIter, maxDiameter):
	dst       = 0
	diameter  = -1
	bailout   = 10000.0 if flags & _F_POTENTIAL else 4.0

	# Set initial values for calculation
	D = complex(1.0)
	Z = C

	if maxDiameter > 0: orbit = np.zeros(maxDiameter, dtype=np.float64)

	for i in range(1, maxIter+1):
		nZ = Z.real * Z.real + Z.imag * Z.imag
		if nZ > bailout: break
		Z = Z * Z + C

		if flags & _F_DISTANCE: D = Z * D * 2.0 + 1

		if maxDiameter > 0:
			orbIdx = i % maxDiameter
			startIdx = maxDiameter-1 if i>= maxDiameter else orbIdx-1
			for n in range(startIdx, -1, -1):
				if abs(orbit[n] - nZ) < 1e-10:
					diameter = orbIdx-n if orbIdx > n else orbIdx+maxDiameter-n
					i = maxIter
					break
			orbit[orbIdx] = nZ

	if flags & _F_DISTANCE:
		aZ = abs(Z)
		dst = sqrt(aZ / abs(D)) * 0.5 * log(aZ)
		# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
		# distance = aZ / abs(distance) * 2.0 * log(aZ)
		# Convert to value between 0 and 1:
		# np.tanh(distance*resolution/size)

	return col.mapColorValue(P, i, maxIter)

@nb.guvectorize([(nb.complex128[:], nb.uint8[:,:], nb.int32, nb.int32, nb.int32, nb.uint8[:,:])], '(n),(i,j),(),(),() -> (n,j)', nopython=True, cache=True, target='parallel')
def calculateVectorZ2(C, P, flags, maxIter, maxDiameter, R):
	for p in range(C.shape[0]):
		R[p,:] = calculatePointZ2(C[p], P, flags, maxIter, maxDiameter)

