
import math

#####################################################################
# Calculation and color mapping constants
#####################################################################

# Colorization modes
FC_ITERATIONS = 0         # Colorize by iterations
FC_DISTANCE   = 1         # Colorize by distance to mandelbrot set
FC_POTENTIAL  = 2         # Colorize by potential

# Color palette modes for iteration-based colorization (FC_ITERATIONS)
FP_LINEAR = 0             # Linear color mapping to selected rgb palette
FP_MODULO = 1             # Color mapping by modulo division to selected rgb palette
FP_HUE    = 2             # Color mapping to hsv/hsl color space based on 1st palette entry
FP_HUEDYN = 3             # Color mapping to hsv/hsl color space, hue based on iterations
FP_LCHDYN = 4
FP_BERNSTEIN = 5          # Bernstein polynomial color mapping

# Colorization options
FO_ORBITS        = 1      # Draw orbits
FO_INSIDE_DIST   = 2      # Distance inside set
FO_SIMPLE_3D     = 4      # Colorize by distance with 3D shading
FO_BLINNPHONG_3D = 8      # Blinn/Phong 3D shading

FO_SHADING       = 12     # Bitmask: Combination of FO_BLINNPHONG_3D, FO_SIMPLE_3D
FO_NOSHADING     = 3      # Bitmask: No 3D shading


#####################################################################
# Numeric constants
#####################################################################

NC_PI12 = math.pi / 2.0
NC_PI2  = math.pi * 2.0
NC_LOG2 = math.log(2.0)
NC_1_LOG2 = 1.0 / NC_LOG2
