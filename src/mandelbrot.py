
import time

import numpy as np
import numba as nb

from math import *
import fractal as frc

import colors as col

_F_POTENTIAL = 1
_F_DISTANCE  = 2

class Mandelbrot(frc.Fractal):

	_defaults = (
		('flags', 0),
		('maxIter', 256),
		('corner', complex(-2.0, -1.5)),
		('size', complex(3.0, 3.0)),
		('maxDiameter', 10)
	)

	_parameterNames = ( 'flags', 'maxIter', 'corner', 'size', 'maxDiameter' )
	_resultNames    = ( 'maxIter', 'iterations', 'Z', 'distance' )

	def __init__(self, corner: complex = complex(-2.0, -1.5) , size: complex = complex(3.0, 3.0), maxIter: int = 256, flip = False):
		super().__init__(size.real, size.imag, corner.real, corner.imag, flip)

		self.maxDiameter   = 10

		# Calculate zoom factor
		defSize = self.getDefaultValue('size')
		self.zoom = max(defSize.real / size.real, defSize.imag / size.imag)

		if maxIter == -1:
			self.maxIter = max(int(abs(1000 * log(1 / sqrt(self.zoom)))), 256)
		else:
			self.maxIter = maxIter

	def getDefaults(self) -> tuple:
		return Mandelbrot._defaults
	
	def getParameterNames(self) -> tuple:
		return Mandelbrot._parameterNames
	
	def getCalcParameters(self) -> tuple:
		maxIter = 4096 if self.flags & _F_DISTANCE else self.maxIter
		return (self.flags, maxIter, self.maxDiameter)
	
	def getMaxValue(self):
		return self.maxIter
	
# Iterate complex point
# Return tuple with results
@nb.njit(cache=True)
def iterate(C, flags, maxIter, maxDiameter):
	dst       = 0
	diameter  = -1
	bailout   = 10000.0 if flags & _F_POTENTIAL else 4.0

	# Set initial values for calculation
	D = complex(1.0)
	Z = C

	if maxDiameter > 0: orbit = np.zeros(maxIter, dtype=np.float32)

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
			orbit[i] = nZ

	if flags & _F_DISTANCE:
		aZ = abs(Z)
		dst = sqrt(aZ / abs(D)) * 0.5 * log(aZ)
		# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
		# distance = aZ / abs(distance) * 2.0 * log(aZ)
		# Convert to value between 0 and 1:
		# np.tanh(distance*resolution/size)

	# if i < maxIter and flags & _F_POTENTIAL:
	#	potential = min(max(0.5*log(nZ)/pow(2.0,float(i)), 0.0), 1.0)
	# We do not return potential. Can be calculated from other results
	return maxIter, i, Z, diameter, dst
	
@nb.guvectorize([(nb.complex64[:], nb.uint8[:,:], nb.int32, nb.int32, nb.int32, nb.uint8[:,:,:])], '(n),(n,n),(),(),() -> (n,n,n)', nopython=True, cache=True, target='cpu')
def calculateArray(C, P, flags, maxIter, maxDiameter, COL):
	for p in range(C.shape[0]):
		dst       = 0
		diameter  = -1
		bailout   = 10000.0 if flags & _F_POTENTIAL else 4.0

		# Set initial values for calculation
		distance  = complex(1.0)
		c = C[p]
		z = c

		if maxDiameter > 0: orbit = np.zeros(maxIter, dtype=np.float32)

		for i in range(1, maxIter+1):
			nz = z.real*z.real+z.imag*z.imag
			if nz > bailout: break
			z = z * z + c

			if flags & _F_DISTANCE: distance = z * distance * 2.0 + 1

			if maxDiameter > 0 and i > 0:
				orbIdx = i % maxDiameter
				startIdx = maxDiameter-1 if i>= maxDiameter else orbIdx-1
				for n in range(startIdx, -1, -1):
					if abs(orbit[n] - nz) < 1e-10:
						diameter = orbIdx-n if orbIdx > n else orbIdx+maxDiameter-n
						i = maxIter
						break
				orbit[i] = nz

		if flags & _F_DISTANCE:
			az = sqrt(nz)
			dst = sqrt(az / abs(distance)) * 0.5 * log(az)
			# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
			# distance = aZ / abs(distance) * 2.0 * log(aZ)
			# Convert to value between 0 and 1:
			# np.tanh(distance*resolution/size)

			# if i < maxIter and flags & _F_POTENTIAL:
			#	potential = min(max(0.5*log(nZ)/pow(2.0,float(i)), 0.0), 1.0)
			# We do not return potential. Can be calculated from other results

		COL[p] = col.mapColorValue(P, i, maxIter, 0)
		# M[p] = maxIter	# Maximum number of iterations
		# I[p] = i		# Iterations
		#Z[p] = nz		# norm(Zn)
		#O[p] = diameter	# Orbit diameter
		#D[p] = dst		# Distance to Mandelbrot set



