
#
# Calculation of Mandelbrot set
#
# References:
#
#   - Orbit detection: https://observablehq.com/@mcmcclur/orbit-detection-for-the-mandelbrot-set
#   - Blinn/Phong shading: https://github.com/jlesuffleur/gpu_mandelbrot/blob/master/mandelbrot.py
#

import math

import numpy as np
import numba as nb

import fractal as frc
import colors as col
import tkconfigure.tkconfigure as tkc

from constants import *


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

	# Reset to initial parameters
	def reset(self):
		self.settings.setValues(sync=True, corner=complex(-2.25, -1.5), size=complex(3.0, 3.0), maxIter=500)

	def getParameterNames(self) -> list:
		return self.settings.getIds()

	def getMaxValue(self):
		maxIter, colorOptions, colorize = self.settings.getValues(['maxIter', 'colorOptions', 'colorize'])

		if colorOptions & FO_ORBITS: maxIter = max(maxIter, 1000)
		if colorize == FC_DISTANCE or colorize == FC_POTENTIAL: maxIter = max(maxIter, 4096)

		return maxIter

	def getCalcParameters(self) -> tuple:
		maxIter = self.getMaxValue()
		return super().getCalcParameters()+(maxIter,)

	###############################################################################
	#
	# Calculate reference points
	#
	#   C - Point in the complex plain
	#   maxIter - Maximum number of iterations
	#   bailout - Bailout radius
	#
	# Returns:
	#
	#  Array with reference points.
	#
	###############################################################################
	def perturbationReference(self, C: complex, maxIter: int, bailout: float) -> np.ndarray:
		R = np.zeros((maxIter+1,), dtype=np.complex128)
		Z = complex(0.0, 0.0)

		for i in range(maxIter+1):
			R[i] = Z
			Z = Z * Z + C

			nZ = Z.real * Z.real + Z.imag * Z.imag
			if nZ > bailout:
				break

		return R[:i]

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
#      FC_ITERATIONS - Number of iterations
#      FC_DISTANCE   - Distance to mandelbrot set
#      FC_POTENTIAL  - Potential
#
#   paletteMode - How to map calculation result to color palette:
#      FP_LINEAR - Linear mapping
#      FP_MODULO - Mapping by modulo division
#      FP_HUE - Mapping to HSB colorspace with hue = P[0,0], saturation P[0,1]
#      FP_HUEDYN - Mapping to HSB colorspace with calculated hue value
#      FP_LCHDYN - Mapping to LCH colorspace with calculated values
#
#   colorOptions - Combination of flags for modifying color calculation:
#      _F_ORBITS - Colorize orbits inside mandelbrot set
#      _F_STRIPES - Draw stripes
#      _F_SIMPLE_3D - Simple 3D shading (cannot be combined with _F_BLINNPHONG_3D)
#      _F_BLINNPHONG_3D - Blinn-Phong 3D shading (cannot be combinded with _F_SIMPLE_3D)
#
#   maxIter - Maximum number of iterations
#
#   bailoutPar - Bailout parameters:
#      [0] = bailoug radius
#      [1] = 2/log(bailout)
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
def calculatePointZ2(C: complex, P: np.ndarray, colorize: int, paletteMode: int, colorOptions: int, maxIter: int, bailoutPar: list[float],
					 colorPar: list[float], light: list[float]) -> np.ndarray:
	stripe_s, stripe_sig, step_s, ncycle, diag = colorPar
	bailout, log_2_bailout = bailoutPar

	diaScale = maxIter/10.0

	dist = 0.0
	pot = 0.0
	stripe_a = 0.0
	one_minus_stripe_sig = 1.0 - stripe_sig

	bStripe = stripe_s > 0 and colorOptions & FO_SHADING
	bOrbits = colorOptions & FO_ORBITS

	Z = 0
	nZ1 = 0.0               # Old value of abs(Z) ** 2 for fast orbit detection
	period = 0              # Period counter for fast orbit detection
	D = complex(1.0, 0.0)   # 1st derivation of Z
	smooth_i = 0			# Smooth iteration counter
	potf = 0.5              # Potential factor 1/2^N

	if bOrbits:
		orbits = np.zeros(maxIter, dtype=np.complex128)

	for i in range(0, maxIter+1):

		Z = Z * Z + C

		if bStripe:
			stripe_t = (math.sin(stripe_s * math.atan2(Z.imag, Z.real)) + 1) * 0.5

		nZ = Z.real * Z.real + Z.imag * Z.imag
		if nZ > bailout:
			aZ = math.sqrt(nZ)   # abs(Z)
			log_aZ = math.log(aZ)

			# Smooth iteration counter
			# log_2_bailout = 2 / log(bailout)
			# NC_1_LOG2 = 1 / log(2)
			log_ratio = log_aZ * log_2_bailout
			smooth_i = 1.0 - math.log(log_ratio) * NC_1_LOG2

			# Exterior distance to mandelbrot set
			dist = aZ * log_aZ / abs(D) / 2

			# Calculate potential
			# pot = log(abs(Z)) / 2 ^ N
			# potf = 1 / 2 ^ N
			pot = log_aZ * potf

			if bStripe:
				stripe_a = (stripe_a * (1 + smooth_i * (stripe_sig-1)) + stripe_t * smooth_i * one_minus_stripe_sig)
				stripe_a = stripe_a / (1 - stripe_sig**i * (1 + smooth_i * (stripe_sig-1)))

			# Color mapping
			mapColorPar = [stripe_a, step_s, ncycle, float(maxIter), pot]
			return frc.mapColorValue(P, float(i+smooth_i), nZ, Z/D, dist/diag, mapColorPar, light, colorize, paletteMode, colorOptions)

		if bOrbits:
			# Search for orbits (full periodicity check)
			idx = frc.findOrbit(orbits[:i], Z, 1e-15, 1e-11)
			if idx > -1:
				# Found orbit, colorize point inside mandelbrot set
				#palIdx = int((i - idx) / maxIter * (P.shape[0]-2))
				#color = P[palIdx]
				#return (color * 255).astype(np.uint8)
				return col.rgb2rgbi(col.hsb2rgb(min(1.0,(i - idx) / maxIter * diaScale), 1.0, 1 - i / maxIter))
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
			stripe_a = stripe_a * stripe_sig + stripe_t * one_minus_stripe_sig

		# Derivation of Z
		D = D * 2 * Z + 1

		potf *= 0.5

	return col.rgb2rgbi(P[-1])

###############################################################################
#
# Iterate complex point with perturbation method using standard Mandelbrot
# formular Z = Z * Z + C
#
# Parameters:
#
#   DC - Distance to reference point in complex plain
#
#   P - Color palette np.array((n, 3), dtype=float64), rgb range = 0-1
#
#   colorize - Value to be used for color calculation:
#      FC_ITERATIONS - Number of iterations
#      FC_DISTANCE   - Distance to mandelbrot set
#      FC_POTENTIAL  - Potential
#
#   paletteMode - How to map calculation result to color palette:
#      FP_LINEAR - Linear mapping
#      FP_MODULO - Mapping by modulo division
#      FP_HUE - Mapping to HSB colorspace with hue = P[0,0], saturation P[0,1]
#      FP_HUEDYN - Mapping to HSB colorspace with calculated hue value
#      FP_LCHDYN - Mapping to LCH colorspace with calculated values
#
#   colorOptions - Combination of flags for modifying color calculation:
#      _F_ORBITS - Colorize orbits inside mandelbrot set
#      _F_STRIPES - Draw stripes
#      _F_SIMPLE_3D - Simple 3D shading (cannot be combined with _F_BLINNPHONG_3D)
#      _F_BLINNPHONG_3D - Blinn-Phong 3D shading (cannot be combinded with _F_SIMPLE_3D)
#
#   maxIter - Maximum number of iterations
#
#   bailoutPar - Bailout parameters:
#      [0] = bailoug radius
#      [1] = 2/log(bailout)
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
#
# References:
#
#   https://philthompson.me/2022/Perturbation-Theory-and-the-Mandelbrot-set.html
#   https://fractalforums.org/index.php?topic=4360.0
#
###############################################################################
@nb.njit(cache=False)
def calculatePointZ2Pert(DC: complex, RO: np.ndarray, P: np.ndarray, colorize: int, paletteMode: int, colorOptions: int, maxIter: int, bailoutPar: list[float],
					     colorPar: list[float], light: list[float]) -> np.ndarray:
	stripe_s, stripe_sig, step_s, ncycle, diag = colorPar
	bailout, log_2_bailout = bailoutPar

	diaScale = maxIter/10.0

	dist = 0.0
	pot = 0.0
	stripe_a = 0.0
	one_minus_stripe_sig = 1.0 - stripe_sig

	bStripe = stripe_s > 0 and colorOptions & FO_SHADING
	bOrbits = colorOptions & FO_ORBITS

	Z = 0
	dZ = 0
	refidx = 0
	maxRefIter = RO.shape[0] - 1
	nZ1 = 0.0               # Old value of abs(Z) ** 2 for fast orbit detection
	period = 0              # Period counter for fast orbit detection
	D = complex(1.0, 0.0)   # 1st derivation of Z
	smooth_i = 0			# Smooth iteration counter
	potf = 0.5              # Potential factor 1/2^N

	if bOrbits:
		orbits = np.zeros(maxIter, dtype=np.complex128)

	for i in range(0, maxIter+1):
        # dz = 2 * refOrbit[ri] * dz + dz * dz + dc
        # We could optimize the above line by using precomputed refOrbit2 (already multiplied by 2)
		dZ = 2.0 * RO[refidx] * dZ + dZ * dZ + DC
		refidx += 1
 
		# Add the delta orbit to the reference orbit
		Z = RO[refidx] + dZ
		
		if bStripe:
			stripe_t = (math.sin(stripe_s * math.atan2(Z.imag, Z.real)) + 1) * 0.5

		nZ = Z.real * Z.real + Z.imag * Z.imag
		if nZ > bailout:
			aZ = math.sqrt(nZ)   # abs(Z)
			log_aZ = math.log(aZ)

			# Smooth iteration counter
			# log_2_bailout = 2 / log(bailout)
			# NC_1_LOG2 = 1 / log(2)
			log_ratio = log_aZ * log_2_bailout
			smooth_i = 1.0 - math.log(log_ratio) * NC_1_LOG2

			# Exterior distance to mandelbrot set
			dist = aZ * log_aZ / abs(D) / 2

			# Calculate potential
			# pot = log(abs(Z)) / 2 ^ N
			# potf = 1 / 2 ^ N
			pot = log_aZ * potf

			if bStripe:
				stripe_a = (stripe_a * (1 + smooth_i * (stripe_sig-1)) + stripe_t * smooth_i * one_minus_stripe_sig)
				stripe_a = stripe_a / (1 - stripe_sig**i * (1 + smooth_i * (stripe_sig-1)))

			# Color mapping
			mapColorPar = [stripe_a, step_s, ncycle, float(maxIter), pot]
			return frc.mapColorValue(P, float(i+smooth_i), nZ, Z/D, dist/diag, mapColorPar, light, colorize, paletteMode, colorOptions)

		if bOrbits:
			# Search for orbits (full periodicity check)
			idx = frc.findOrbit(orbits[:i], Z, 1e-15, 1e-11)
			if idx > -1:
				# Found orbit, colorize point inside mandelbrot set
				#palIdx = int((i - idx) / maxIter * (P.shape[0]-2))
				#color = P[palIdx]
				#return (color * 255).astype(np.uint8)
				return col.rgb2rgbi(col.hsb2rgb(min(1.0,(i - idx) / maxIter * diaScale), 1.0, 1 - i / maxIter))
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
			stripe_a = stripe_a * stripe_sig + stripe_t * one_minus_stripe_sig

		# If the delta is larger than the reference, or if the reference orbit has already escaped,
		# reset back to the beginning of the SAME reference orbit!
		if aZ < abs(dZ) or refidx == maxRefIter:
			dZ = Z
			refidx = 0

		# Derivation of Z
		D = D * 2 * Z + 1

		potf *= 0.5

	return col.rgb2rgbi(P[-1])

###############################################################################
# Vectorized calculation functions
###############################################################################

@nb.guvectorize([(nb.complex128[:], nb.float64[:,:], nb.int32, nb.int32, nb.int32, nb.float64[:], nb.float64[:], nb.int32, nb.uint8[:,:])], '(n),(i,j),(),(),(),(k),(l),() -> (n,j)', nopython=True, cache=False, target='parallel')
def calculateVectorZ2(C, P, colorize, paletteMode, colorOptions, colorPar, light, maxIter, R):
	bailout = 4.0 if colorize == FC_ITERATIONS and paletteMode != FP_HUE and colorOptions == 0 else 10**10
	log_2_Bailout = 2.0 / math.log(bailout)

	for p in range(C.shape[0]):
		R[p,:] = calculatePointZ2(C[p], P, colorize, paletteMode, colorOptions, maxIter, [bailout, log_2_Bailout], colorPar, light)

@nb.guvectorize([(nb.complex128[:], nb.complex128[:], nb.float64[:,:], nb.int32, nb.int32, nb.int32, nb.float64[:], nb.float64[:], nb.int32, nb.uint8[:,:])], '(n),(n),(i,j),(),(),(),(k),(l),() -> (n,j)', nopython=True, cache=False, target='parallel')
def calculateVectorZ2Pert(DC, RO, P, colorize, paletteMode, colorOptions, colorPar, light, maxIter, R):
	bailout = 4.0 if colorize == FC_ITERATIONS and paletteMode != FP_HUE and colorOptions == 0 else 10**10
	log_2_Bailout = 2.0 / math.log(bailout)

	for p in range(DC.shape[0]):
		R[p,:] = calculatePointZ2Pert(DC[p], RO, P, colorize, paletteMode, colorOptions, maxIter, [bailout, log_2_Bailout], colorPar, light)

