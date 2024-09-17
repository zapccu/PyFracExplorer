
#
# Calculation of Julia set
#
#

import time

import numpy as np
import numba as nb

import math
import cmath

import fractal as frc
import colors as col
import tkconfigure as tkc

# Colorization modes
_C_ITERATIONS = 0         # Colorize by iterations
_C_DISTANCE   = 1         # Colorize by distance to mandelbrot set
_C_POTENTIAL  = 2         # Colorize by potential
_C_SHADING    = 3         # Colorize by distance with 3D shading
_C_BLINNPHONG = 4         # Blinn/Phong 3D shading

# Colorization flags
_F_LINEAR  = 1            # Linear color mapping to selected palette
_F_MODULO  = 2            # Color mapping by modulo division to selected palette
_F_ORBITS  = 4            # Colorize orbits inside mandelbrot set
_F_STRIPES = 8

# Flag masks
_F_NOORBITS = _F_LINEAR | _F_MODULO


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
				},
				"colorize": {
					"inputtype": "int",
					"valrange":  ["Iterations", "Distance", "Potential", "Shading", "Blinn/Phong"],
					"initvalue": 0,
					"widget":    "TKCRadiobuttons",
					"widgetattr": {
						"text": "Colorization options"
					}
				},
				"flags": {
					"inputtype": "bits",
					"valrange":  ["Linear", "Modulo", "Orbits", "Stripes"],
					"initvalue": 1,
					"widget":     "TKCFlags",
					"widgetattr": {
						"text": "Colorization flags"
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
		return 4096 if self.settings['colorize'] == _C_DISTANCE else self.settings['maxIter']

	def getCalcParameters(self) -> tuple:
		maxIter = self.getMaxValue()
		return (self.settings['point'], self.settings['colorize'], self.settings['flags'], maxIter)

@nb.njit(cache=True)
def findOrbit(O: np.ndarray, Z: complex, tolerance: float):
	for n in range(O.shape[0], -1, -1):
		d = Z - O[n]
		if d.real * d.real + d.imag * d.imag < tolerance:
			return n
	return -1

# Iterate complex point using standard Mandelbrot formular Z = Z * Z + C
# Return color array [red, green, blue]
@nb.njit(cache=True)
def calculatePointZ2(Z, P, C, colorize, flags, bailout, maxIter, light):
	dst = 0.0      # Distance
	pot = 0.0      # Potential
	dia = 0        # Orbit diameter
	diaScale = maxIter/10.0

	D = complex(1.0)   # 1st derivation

	period = 0         # Period counter for simplified orbit detection
	nZ1 = 0.0          # Old value of abs(Z)^2
	pow = 1            # Power of 2 for potential calculation

	if flags & _F_ORBITS:
		# Create array for periodicity check
		orbits = np.zeros(maxIter, dtype=np.complex128)
		orbits[0] = complex(0,0)
		oc = 1

	for i in range(1, maxIter+1):
		nZ = Z.real * Z.real + Z.imag * Z.imag
		if nZ > bailout: break

		if flags & _F_ORBITS:
			# Search for orbits (full periodicity check)
			idx = findOrbit(orbits[:i], Z, 1e-15)
			if idx > -1:
				# Be more tolerant
				idx = findOrbit(orbits[:i], Z, 1e-11)
				dia = i - idx
				return col.hsbToRGB(min(1.0,dia/maxIter*diaScale), 1.0, 1-i/maxIter)
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

		if colorize == _C_DISTANCE or colorize == _C_SHADING or colorize == _C_BLINNPHONG:
			D = D * 2 * Z + 1

		Z = Z * Z + C

		pow *= 2

	if i < maxIter:
		if colorize == _C_ITERATIONS:
			return col.mapColorValue(P, float(i), maxIter, colorize, flags & _F_NOORBITS)
		
		if colorize == _C_DISTANCE:
			aZ = abs(Z)
			dst = math.sqrt(aZ / abs(D)) * 0.5 * math.log(aZ)
			# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
			# distance = aZ / abs(distance) * 2.0 * log(aZ)
			# Convert to value between 0 and 1:
			# np.tanh(distance*resolution/size)
			return col.mapColorValue(P, dst, maxIter, colorize, flags & _F_NOORBITS)

		elif colorize == _C_POTENTIAL:
			# pot = log(nZ)/pow
			logZn = math.log(nZ)/2.0
			pot = math.log(logZn / math.log(2)) / math.log(2)
			return col.mapColorValue(P, pot, maxIter, colorize, flags & _F_NOORBITS)
		
		elif colorize == _C_SHADING:
			h2 = 1.5    # height factor of the incoming light
			angle = 45  # incoming direction of light
			v = cmath.exp(complex(0,1) * angle * 2 * math.pi / 360)  # unit 2D vector in this direction
			u = Z / D
			u /= abs(u)  # normal vector: (u.re,u.im,1) 
			t = u.real * v.real + u.imag * v.imag + h2  # dot product with the incoming light
			t /= (1 + h2)  # rescale so that t does not get bigger than 1
			return col.mapColorValue(P, max(t,0), maxIter, colorize, flags & _F_NOORBITS)
		
		elif colorize == _C_BLINNPHONG:
			u = Z / D
			b = col.phong(u, light)
			return col.mapColorValue(P, b, maxIter, colorize, flags & _F_NOORBITS)

	return col.mapColorValue(P, float(i), maxIter, colorize, flags & _F_NOORBITS)

@nb.guvectorize([(nb.complex128[:], nb.uint8[:,:], nb.complex128, nb.int32, nb.int32, nb.int32, nb.uint8[:,:])], '(n),(i,j),(),(),(),() -> (n,j)', nopython=True, cache=True, target='parallel')
def calculateVectorZ2(Z, P, C, colorize, flags, maxIter, R):
	bailout = 10000.0 if colorize == _C_POTENTIAL or colorize == _C_SHADING or colorize == _C_BLINNPHONG else 4.0
	if flags & _F_ORBITS: maxIter = max(maxIter, 1000)

	# Light source for phong shading
	light = [45., 45., .75, .2, .5, .5, 20]
	light[0] = 2*math.pi*light[0]/360
	light[1] = math.pi/2*light[1]/90

	for p in range(Z.shape[0]):
		R[p,:] = calculatePointZ2(Z[p], P, C, colorize, flags, bailout, maxIter, light)

