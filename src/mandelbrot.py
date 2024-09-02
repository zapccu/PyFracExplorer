
import time

import numpy as np
import numba as nb

from math import *
import cmath

import fractal as frc
import colors as col
import tkconfigure as tkc


# Flags
_F_ITERLINEAR = 1
_F_ITERMODULO = 2
_F_ORBITCOLOR = 4   # Colorize orbits
_F_POTENTIAL  = 8   # Colorize by fractal potential
_F_DISTANCE   = 16  # Colorize by fractal distance
_F_SHADING    = 32


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
					"valrange":  (0, 20),
					"initvalue": 20,
					"widget":    "TKCSpinbox",
					"label":     "Max. diameter",
					"width":     6
				},
				"flags": {
					"inputtype": "bits",
					"valrange":  ["Linear", "Modulo", "Orbits", "Potential", "Distance"],
					"initvalue": 1,
					"widget":     "TKCFlags",
					"widgetattr": {
						"text": "Colorization options"
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

@nb.njit(cache=True)
def calculatePoint3D(C, P, flags, maxIter, maxDiameter):
	h2 = 1.5  # height factor of the incoming light
	angle = 45  # incoming direction of light
	v = cmath.exp(complex(0,1) * angle * 2 * pi / 360)  # unit 2D vector in this direction
	# incoming light 3D vector = (v.re,v.im,h2)

	bailout = 10000.0  # do not take bailout too small

	Z = C
	dc = complex(1, 0)
	der = dc

	for i in range(0, maxIter+1):
		nZ = Z.real * Z.real + Z.imag * Z.imag
		if nZ > bailout: break

		der = der * 2 * Z + dc
		Z = Z * Z + C

	if i >= maxIter:
		return np.array([0, 0, 0], dtype=np.uint8)
	else:
		u = Z / der
		u = u / abs(u)  # normal vector: (u.re,u.im,1) 
		t = u.real * v.real + u.imag * v.imag + h2  # dot product with the incoming light
		t = t / (1 + h2)  # rescale so that t does not get bigger than 1
		if t < 0: t=0
		color = int(255 * t)
		return np.array([color, color, color], dtype=np.uint8)

# Iterate complex point
# Return tuple with results
@nb.njit(cache=True)
def calculatePointZ2(C, P, flags, maxIter, maxDiameter):
	dst       = 0.0
	pot       = 0.0
	diameter  = -1
	bailout   = 10000.0 if flags & _F_POTENTIAL else 4.0

	# Set initial values for calculation
	D = complex(1.0)
	Z = C

	# if maxDiameter > 0: orbit = np.zeros(maxDiameter, dtype=np.float64)
	period = 0
	nZ1 = 0.0
	# pow = 1

	for i in range(1, maxIter+1):
		nZ = Z.real * Z.real + Z.imag * Z.imag
		if nZ > bailout: break

		Z = Z * Z + C

		if flags & _F_DISTANCE: D = Z * D * 2.0 + 1

		if abs(nZ - nZ1) < 1e-10:
			i = maxIter
			break
		else:
			period += 1
			if period > maxDiameter:
				period = 0
				nZ1 = nZ

		# pow *= 2

	if i < maxIter:
		if flags & _F_DISTANCE:
			aZ = abs(Z)
			dst = sqrt(aZ / abs(D)) * 0.5 * log(aZ)
			# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
			# distance = aZ / abs(distance) * 2.0 * log(aZ)
			# Convert to value between 0 and 1:
			# np.tanh(distance*resolution/size)
			return col.mapColorValue(P, dst, maxIter, flags)

		if flags & _F_POTENTIAL:
			# pot = log(nZ)/pow
			logZn = log(nZ)/2.0
			pot = log(logZn / log(2)) / log(2)
			return col.mapColorValue(P, pot, maxIter, flags)

	return col.mapColorValue(P, float(i), maxIter, flags)

@nb.guvectorize([(nb.complex128[:], nb.uint8[:,:], nb.int32, nb.int32, nb.int32, nb.uint8[:,:])], '(n),(i,j),(),(),() -> (n,j)', nopython=True, cache=True, target='parallel')
def calculateVectorZ2(C, P, flags, maxIter, maxDiameter, R):
	for p in range(C.shape[0]):
		# R[p,:] = calculatePointZ2(C[p], P, flags, maxIter, maxDiameter)
		R[p,:] = calculatePoint3D(C[p], P, flags, maxIter, maxDiameter)

@nb.guvectorize([(nb.float64[:,:], nb.uint8[:,:], nb.int32, nb.int32,  nb.uint8[:,:])], '(n,m),(i,j),(),(),(n,k)', nopython=True, cache=True, target='parallel')
def colorize(R, P, maxValue, flags, I):
	for p in range(R.shape[0]):
		I[p,:] = col.mapColorValueNew(P, R[p], maxValue, flags)
