
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

		self.settings = tkc.TKConfigure({
			"Mandelbrot Set": {
				"corner": {
					"inputType": "complex",
					"initValue": corner,
					"widget":    "TKCEntry",
					"label":     "Corner"
				},
				"size": {
					"inputType": "complex",
					"initValue": size,
					"widget":    "TKEntry",
					"label":     "Size"
				},
				"maxIter": {
					"inputType": "int",
					"valRange":  (10, 4000, 50),
					"initValue": maxIter,
					"widget":    "TKCSpinbox",
					"label":     "Max. iterations"
				},
				"maxDiameter": {
					"inputType": "int",
					"valRange":  (0, 10),
					"initValue": 10,
					"widget":    "TKCSpinbox",
					"label":     "Max. diameter"
				},
				"flags": {
					"inputType": "int",
					"valRange":  ["Potential", "Distance"],
					"initValue": 0,
					"wiget":     "TKCFlags",
					"widgetAttr": {
						"text": "Calculation options"
					}
				}
			}
		})

		# Calculate zoom factor
		defSize = self.settings['size']
		self.zoom = max(defSize.real / size.real, defSize.imag / size.imag)

		if maxIter == -1:
			self.maxIter = min(max(int(abs(1000 * log(1 / sqrt(self.zoom)))), 256), 4096)
		else:
			self.maxIter = maxIter

	def getParameterNames(self) -> list:
		return self.settings.getIds()
	
	def getCalcParameters(self) -> tuple:
		maxIter = 4096 if self.flags & _F_DISTANCE else self.maxIter
		return (self.flags, maxIter, self.maxDiameter)
	
	def getMaxValue(self):
		return 4096 if self.flags & _F_DISTANCE else self.maxIter

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

