
from tkinter import *
from gui import *

import colors as col
import fractal as frc
import mandelbrot as man
import julia as jul

from drawer import *
from coloreditor import *

import tkconfigure as tkc


class Application:

	def __init__(self, width: int, height: int, title: str):

		self.colorTable = {
			'Monochrome':   col.createLinearPalette(4096),
			'Grey':         col.createLinearPalette(4096, [col.rgbf(80, 80, 80), (1.,1.,1.)], defColor=(0., 0., 0.)),
			'Sinus':        col.createSinusPalette(4096, defColor=(0, 0, 0)),
			'SinusCosinus': col.createSinusCosinusPalette(4096, defColor=(0, 0, 0)),
			'RedGreenBlue': col.createLinearPalette(4096, [col.rgbf(125,30,0),col.rgbf(30,255,30),col.rgbf(0,30,125)]),
			'BlueGrey':     col.createLinearPalette(4096, [col.rgbf(100,100,100),col.rgbf(200,200,200),col.rgbf(0,0,255)]),
			'Preset':       col.createSinusPalette(4096, defColor=(0, 0, 0))
		}

		# Settings
		self.settings = tkc.TKConfigure({
			"Image parameters": {
				"imageWidth": {
					'inputtype': 'int',
					'valrange':  (100, 4096, 100),
					'initvalue': 800,
					'widget':    'TKCSpinbox',
					'label':     'Width',
					'width':     8,
					'row':       0,
					'column':    0
				},
				"imageHeight": {
					'inputtype': 'int',
					'valrange':  (100, 4096, 100),
					'initvalue': 800,
					'widget':    'TKCSpinbox',
					'label':     'Height',
					'width':     8,
					'row':       0,
					'column':    1
				}
			},
			"Fractal selection": {
				"preset": {
					'inputtype': 'str',
					'valrange':  ['None'] + list(frc.presets.keys()),
					'initvalue': 'None',
					'widget':    'TKCListbox',
					'label':     'Preset',
					'width':     15,
					'notify':    self.onPresetSelected
				},
				"fractalType": {
					'inputtype': 'str',
					'valrange':  [
						'Mandelbrot Set', 'Julia Set'
					],
					'initvalue': 'Mandelbrot Set',
					'widget':    'TKCListbox',
					'label':     'Fractal type:',
					'width':     15,
					'widgetattr': {
						'justify': 'left'
					},
					'notify':    self.onFractalTypeChanged
				},
				"drawMode": {
					'inputtype': 'str',
					'valrange':  [
						'Vectorized', 'SQEM Recursive', 'SQEM Linear'
					],
					'initvalue': 'Vectorized',
					'widget':    'TKCListbox',
					'label':     'Draw mode:',
					'width':     15,
					'widgetattr': {
						'justify': 'left'
					},
				},
				'colorPalette': {
					'inputtype': 'str',
					'valrange':  list(self.colorTable.keys()),
					'initvalue': 'Grey',
					'widget':    'TKCListbox',
					'label':     'Color palette:',
					'width':     15,
					'widgetattr': {
						'justify': 'left'
					}
				}
			}
		})

		# Default fractal
		self.fractal = man.Mandelbrot(complex(-2.25, -1.5), complex(3.0, 3.0))
		# self.fractal = man.Mandelbrot(complex(-0.42125, -1.21125), complex(0.62249, 0.62249), maxIter=500)

		# Create GUI
		self.gui = GUI(self, title, width, height, statusHeight=50, controlWidth=300)

		# Create settings widgets
		self.fractalRow = self.settings.createMask(self.gui.controlFrame, startrow=self.gui.controlFrame.nextRow(), padx=2, pady=3)
		self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

		# We want to be notified if fractal type selection changed
		# self.settings.notify(onchange=self.onSettingsChanged)

		# Define selection handler
		self.gui.setSelectionHandler(self.onPointSelected, self.onAreaSelected)



	def __getitem__(self, index: str):
		return self.settings.get(index)
	
	def run(self):
		self.gui.mainWindow.mainloop()

	def update(self):
		self.gui.mainWindow.update()

	#
	# Screen selection handling
	#

	def onPointSelected(self, x, y):
		print(f"Selected point {x}, {y}")

	def onAreaSelected(self, x1, y1, x2, y2):
		print(f"Selected area: {x1},{y1} - {x2},{y2}")

	#
	# Command handling
	#
	
	# Apply button pressed
	def onApply(self):
		imageWidth  = self.settings['imageWidth']
		imageHeight = self.settings['imageHeight']

		if self.gui.selection.isAreaSelected():
			# Zoom in
			x1, y1, x2, y2 = self.gui.selection.getArea()
			size   = self.fractal.mapWH(x2-x1+1, y2-y1+1, imageWidth, imageHeight)
			corner = self.fractal.mapXY(x1, y1, imageWidth, imageHeight)
			self.fractal.setDimensions(corner, size)

		elif self.gui.selection.isPointSelected():
			if self.settings['fractalType'] == 'Mandelbrot Set':
				# Calculate Julia set at selected point
				x, y = self.gui.selection.getPoint()
				point = self.fractal.mapXY(x, y, imageWidth, imageHeight)
				self.settings.set('fractalType', 'Julia Set', sync=True)
				self.fractal.settings.deleteMask()
				self.fractal = jul.Julia(point=point)
				self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)
		else:
			self.settings.apply()
			self.fractal.settings.apply()

	# Draw button pressed
	def onDraw(self):
		self.gui.drawFrame.clearCanvas()
		self.gui.selection.reset()

		self.gui.statusFrame.setFieldValue('drawing', 'Drawing ...')
		self.onStatusUpdate({'drawing': 'Drawing ...'})
		w = self.settings['imageWidth']
		h = self.settings['imageHeight']
		self.draw = Drawer(self, w, h)
		self.draw.drawFractal(self.fractal, 0, 0, w, h, onStatus=self.onStatusUpdate)
		self.onStatusUpdate({'drawing': "{:.2f} s".format(self.draw.calcTime)})
		
		self.gui.selection.enable()

	# Cancel button pressed
	def onCancel(self):
		self.draw.cancel = True

	def onColorEdit(self):
		ce = ColorEditor(self.gui.mainWindow)
		return

	#
	# Event handling
	#

	# Settings changed
	def onPresetSelected(self, oldValue, newValue):
		if newValue != 'None':
			self.fractal.settings.deleteMask()

			preset = frc.presets[newValue]
			if 'corner' in preset and 'size' in preset:
				corner = preset['corner']
				size   = preset['size']
			else:
				corner = complex(preset['coord'][0], preset['coord'][2])
				size   = complex(preset['coord'][1]-preset['coord'][0], preset['coord'][3]-preset['coord'][2])

			if frc.presets[newValue]['type'] == 'Mandelbrot':
				self.fractal = man.Mandelbrot(corner, size, maxIter=preset['maxIter'], stripes=preset['stripes'],
								  steps=preset['steps'], ncycle=preset['ncycle'])
			else:
				self.fractal = jul.Julia()

			self.fractal.settings.setValues(colorize=preset['colorize'], colorOptions=preset['colorOptions'])

			# Dynamically create color palette
			palette = preset['palette']
			fnc = col.paletteFunctions[palette['type']]
			self.colorTable['Preset'] = fnc(palette['size'], **palette['par'])
			self.settings.set('colorPalette', 'Preset', sync=True)

			self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)
		elif oldValue != 'None':
			self.fractal.settings.deleteMask()
			self.fractal = man.Mandelbrot()
			self.settings.set('colorPalette', 'Grey', sync=True)
			self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

	def onFractalTypeChanged(self, oldValue, newValue):
		self.fractal.settings.deleteMask()
		if newValue == 'Mandelbrot Set':
			self.fractal = man.Mandelbrot()
		else:
			self.fractal = jul.Julia()
		self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

	# Status updates
	def onStatusUpdate(self, statusInfo: dict):
		if 'drawing' in statusInfo:
			self.gui.statusFrame.setFieldValue('drawing', statusInfo['drawing'])
		if 'progress' in statusInfo:
			self.gui.statusFrame.setFieldValue('progress', statusInfo['progress'])
			# self.gui.statusFrame.setProgress(statusInfo['progress'])
		if 'update' not in statusInfo or statusInfo['update'] == True:
			self.gui.mainWindow.update()
