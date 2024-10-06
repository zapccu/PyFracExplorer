
from tkinter import *
from tkinter import filedialog as fd
from gui import *

import colors as col
import presets as ps
import fractal as frc
import mandelbrot as man
import julia as jul

from drawer import *

import tkconfigure as tkc


class Application:

	def __init__(self, width: int, height: int, title: str):
		colorTables = [ ct['name'] for ct in col.colorTables ]

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
				},
				"autoScale": {
					'inputtype': 'int',
					'valrange':  (0, 1),
					'initvalue': 1,
					'widget':    'TKCCheckbox',
					'label':     'Autoscale',
					'notify':     self.onAutoscale
				}
			},
			"Fractal selection": {
				"preset": {
					'inputtype': 'str',
					'valrange':  ['None'] + list(ps.presets.keys()),
					'initvalue': 'None',
					'widget':    'TKCListbox',
					'label':     'Preset',
					'width':     15,
					'notify':    self.onPresetSelected
				},
				"fractalType": {
					'inputtype': 'str',
					'valrange':  [
						'Mandelbrot', 'Julia'
					],
					'initvalue': 'Mandelbrot',
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
					'valrange':  colorTables,
					'initvalue': 'Grey',
					'widget':    'TKCListbox',
					'label':     'Color palette:',
					'width':     15,
					'widgetattr': {
						'justify': 'left'
					},
					'notify': self.onPaletteChanged
				},
				'colorTable': {
					'inputtype': 'list',
					'initvalue': col.createLinearPalette(300, [(80/255, 80/255, 80/255), (1., 1., 1.)]).tolist(),
					'widget':    'TKCColortable',
					'width':     250
				},
				'defColor': {
					'inputtype': 'str',
					'valrange':  ('^#([0-9a-fA-F]{2}){3}$',),
					'initvalue': '#000000',
					'label':     'Default color',
					'widget':    'TKCColor',
					'width':     80
				}
			}
		})

		# Default fractal
		self.fractal = man.Mandelbrot()

		# Default color palette
		self.palette = 'Grey'

		# Image drawer
		self.draw = None

		# Create GUI
		self.gui = GUI(self, title, width, height, statusHeight=50, controlWidth=400)

		# Create menu
		self.menubar = Menu(self.gui.mainWindow)

		self.fileMenu = Menu(self.menubar, tearoff=0)
		self.fileMenu.add_command(label="Open", command=self.onFileOpen)
		self.fileMenu.add_command(label="Save as", command=self.onFileSaveAs)
		self.fileMenu.add_separator()
		self.fileMenu.add_command(label="Exit", command=self.gui.mainWindow.quit)
		self.menubar.add_cascade(label="File", menu=self.fileMenu)

		self.imageMenu = Menu(self.menubar, tearoff=0)
		self.imageMenu.add_command(label="Save as", state="disabled", command=self.onImageSaveAs)
		self.menubar.add_cascade(label="Image", menu=self.imageMenu)

		self.gui.mainWindow.config(menu=self.menubar)

		# Create settings widgets
		self.fractalRow = self.settings.createMask(self.gui.controlFrame, startrow=self.gui.controlFrame.nextRow(), padx=2, pady=3)
		self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

		# Define selection handler
		self.gui.setSelectionHandler(self.onPointSelected, self.onAreaSelected, self.onSelectionCancelled)

	def __getitem__(self, index: str):
		return self.settings.get(index)
	
	def run(self):
		self.gui.mainWindow.mainloop()

	def update(self):
		self.gui.mainWindow.update()

	# Apply a preset, create fractal and palette, adjust input mask
	def applyPreset(self, preset: dict) -> bool:
		self.fractal.settings.deleteMask()

		if 'corner' in preset and 'size' in preset:
			corner = preset['corner']
			size   = preset['size']
		elif 'coord' in preset:
			corner = complex(preset['coord'][0], preset['coord'][2])
			size   = complex(preset['coord'][1]-preset['coord'][0], preset['coord'][3]-preset['coord'][2])
		else:
			return False

		if preset['type'] == 'Mandelbrot':
			self.fractal = man.Mandelbrot(corner, size, maxIter=preset['maxIter'], stripes=preset['stripes'],
								steps=preset['steps'], ncycle=preset['ncycle'])
		else:
			self.fractal = jul.Julia(preset['point'], corner, size, maxIter=preset['maxIter'], stripes=preset['stripes'],
								steps=preset['steps'], ncycle=preset['ncycle'])

		self.fractal.settings.setValues(colorize=preset['colorize'], colorOptions=preset['colorOptions'])

		col.colorTables['Preset'] = preset['palette']
		self.palette = 'Preset'
		self.settings.setValues(sync=True, colorPalette='Preset', fractalType=preset['type'])

		colorTable = col.createPalette('Preset', size=300).tolist()
		self.settings.set('colorTable', colorTable, sync=True)

		self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

		return True

	#
	# Menu command handling
	#

	# Open fractal definition
	def onFileOpen(self):
		fileTypes = [
			('Fractal definition', '*.frc'),
			('All files', '*')
		]
		fileName = fd.askopenfilename(filetypes=fileTypes)

	# Save fractal definition
	def onFileSaveAs(self):
		fileTypes = [
			('Fractal definition', '*.frc')
		]
		fileName = fd.asksaveasfilename(filetypes=fileTypes)

	# Save image
	def onImageSaveAs(self):
		fileTypes = [('PNG Image', '*.png')]
		fileName = fd.asksaveasfilename(filetypes=fileTypes, initialfile="image.png", defaultextension="png")
		if fileName is not None and self.draw is not None and self.draw.image is not None:
			self.draw.image.save(fileName, "png")

	#
	# Screen selection handling
	#

	def onPointSelected(self, x, y):
		self.gui.controlFrame.btnApply.config(state=NORMAL)
		print(f"Selected point {x}, {y}")

	def onAreaSelected(self, x1, y1, x2, y2):
		self.gui.controlFrame.btnApply.config(state=NORMAL)
		print(f"Selected area: {x1},{y1} - {x2},{y2}")

	def onSelectionCancelled(self):
		self.gui.controlFrame.btnApply.config(state=DISABLED)


	#
	# Command handling
	#
	
	# Apply button pressed
	def onApply(self):
		imageWidth, imageHeight = self.settings.getValues(['imageWidth', 'imageHeight'])

		if self.gui.selection.isAreaSelected():
			# Zoom in
			x1, y1, x2, y2 = self.gui.selection.getArea()
			size   = self.fractal.mapWH(x2-x1+1, y2-y1+1, imageWidth, imageHeight)
			corner = self.fractal.mapXY(x1, y1, imageWidth, imageHeight)
			self.fractal.setDimensions(corner, size)

		elif self.gui.selection.isPointSelected():
			if self.settings['fractalType'] == 'Mandelbrot':
				# Calculate Julia set at selected point
				x, y = self.gui.selection.getPoint()
				point = self.fractal.mapXY(x, y, imageWidth, imageHeight)
				self.settings.set('fractalType', 'Julia', sync=True)
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
		w, h = self.settings.getValues(['imageWidth', 'imageHeight'])
		self.draw = Drawer(self, w, h)
		self.draw.drawFractal(self.fractal, 0, 0, w, h, onStatus=self.onStatusUpdate)
		self.onStatusUpdate({'drawing': "{:.2f} s".format(self.draw.calcTime)})
		
		self.imageMenu.entryconfig('Save as', state="normal")
		self.gui.selection.enable(scalefactor=self.draw.scaleFactor)

	# Cancel button pressed
	def onCancel(self):
		self.draw.cancel = True

	#
	# Widget event handling
	#

	# Autoscale enabled/disabled
	def onAutoscale(self, oldValue, newValue):
		self.draw.showImage(scale=newValue)

	# Fractal preset selected
	def onPresetSelected(self, oldValue, newValue):
		if newValue != 'None':
			# Apply new preset
			self.applyPreset(ps.presets[newValue])

		elif oldValue != 'None':
			# Reset to default
			self.fractal.settings.deleteMask()
			self.fractal = man.Mandelbrot()
			self.settings.set('colorPalette', 'Grey', sync=True)
			self.palette = 'Grey'
			self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

	# Fractal type changed
	def onFractalTypeChanged(self, oldValue, newValue):
		self.fractal.settings.deleteMask()
		if newValue == 'Mandelbrot':
			self.fractal = man.Mandelbrot()
		else:
			self.fractal = jul.Julia()
		self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

	# Color palette changed
	def onPaletteChanged(self, oldValue, newValue):
		self.palette = newValue
		colorTable = col.createPalette(newValue, size=300).tolist()
		self.settings.set('colorTable', colorTable, sync=True)

	# Status updates
	def onStatusUpdate(self, statusInfo: dict):
		if 'drawing' in statusInfo:
			self.gui.statusFrame.setFieldValue('drawing', statusInfo['drawing'])
		if 'progress' in statusInfo:
			self.gui.statusFrame.setFieldValue('progress', statusInfo['progress'])
			# self.gui.statusFrame.setProgress(statusInfo['progress'])
		if 'update' not in statusInfo or statusInfo['update'] == True:
			self.gui.mainWindow.update()
