
from fractal import _C_ITERATIONS, _C_DISTANCE, _C_POTENTIAL, _O_ORBITS, _O_SIMPLE_3D, _O_BLINNPHONG_3D

###############################################################################
# Fractal presets
#
# Some taken from https://github.com/jlesuffleur/gpu_mandelbrot/tree/master
###############################################################################

presets = {
	'crown': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-0.5503295086752807, -0.5503293049351449, -0.6259346555912755, -0.625934541001796],
		'stripes':    2,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.11, .02, .92]
			}
		}
	},
	'pow': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.9854527029227764, -1.9854527027615938, 0.00019009159314173224, 0.00019009168379912058],
		'stripes':    0,
		'steps':      10,
		'ncycle':     8,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.29, .02, 0.9]
			}
		}
	},
	'octogone': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.749289287806423, -1.7492892878054118, -1.8709586016347623e-06, -1.8709580332005737e-06],
		'stripes':    5,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.83, .01, .99]
			}
		}
	},
	'julia': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.9415524417847085, -1.9415524394561112, 0.00013385928801614168, 0.00013386059768851223],
		'stripes':    0,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.87, .83, .77]
			}
		}
	},
	'lightning': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-0.19569582393630502, -0.19569331188751315, 1.1000276413181806, 1.10002905416902],
		'stripes':    8,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.54, .38, .35]
			}
		}
	},
	'web': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.7497082019887222, -1.749708201971718, -1.3693697170765535e-07, -1.369274301311596e-07],
		'stripes':    0,
		'steps':      20,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.47, .51, .63]
			}
		}
	},
	'wave': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.8605721473418524, -1.860572147340747, -3.1800170324714687e-06, -3.180016406837821e-06],
		'stripes':    12,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.6, .57, .45]
			}
		}
	},
	'tiles': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-0.7545217835886875, -0.7544770820676441, 0.05716740181493137, 0.05719254327783547],
		'stripes':    2,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.63, .83, .98]
			}
		}
	},
	'velvet': {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'coord':      [-1.6241199193994318, -1.624119919281773, -0.00013088931048083944, -0.0001308892443058033],
		'stripes':    5,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.29, .52, .59]
			}
		}
	},
	"color-vortex": {
		'type':       'Mandelbrot',
		'maxIter':    5000,
		'corner':     -0.6656224884756315+0.3546631894271655j,
		'size':       0.0018369561502944544+0.0018369561502944544j,
		'stripes':    4,
		'steps':      0,
		'ncycle':     19,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.85, .0, .15]
			}
		}
	},
	"double-swirl": {
		'type':       'Mandelbrot',
		'maxIter':    2000,
		'corner':     -0.6941676462049772+0.2919259663249364j,
		'size':       3.568563540681529e-05+3.568563540681529e-05j,
		'stripes':    2,
		'steps':      0,
		'ncycle':     32,
		'colorize':   _C_DISTANCE,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.85, .0, .15]
			}
		}
	},
	"blue-julia": {
		'type':       'Julia',
		'maxIter':    2000,
		'corner':     -1.5-1.5j,
		'size':       3+3j,
		'point':      -0.7269+0.1889j,
		'stripes':    0,
		'steps':      0,
		'ncycle':     1,
		'colorize':   _C_ITERATIONS,
		'colorOptions': _O_BLINNPHONG_3D,
		'palette': {
			"type": "Sinus",
			'size': 4096,
			'par': {
				'thetas': [.85, .0, .15]
			}
		}
	}
}
