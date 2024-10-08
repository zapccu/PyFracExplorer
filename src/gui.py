
from tkinter import *
from tkinter.ttk import Combobox, Style, Progressbar, Separator
from tkinter.scrolledtext import ScrolledText


"""
GUI

Classes:

  StatusFrame    - Status frame with text labels at the bottom side of the window
  DrawFrame      - Drawing frame with canvas and scrollbars at the top/left side of the window
  ControlFrame   - Control frame with parameter widgets at the right side of the window
  Selection      - Handle selection of points or areas inside the drawing frame canvas

"""

class ProgressBar:

	def __init__(self, parentFrame, maxWidth: int, maxValue: int = 100):
		self.parentFrame = parentFrame
		self.maxWidth = maxWidth
		self.maxValue = maxValue
		self.delta = maxWidth/maxValue
		self.canvas = Canvas(parentFrame, width=maxWidth, height=16)
		self.canvas.pack_propagate(False)
		self.canvas.pack(side=LEFT, expand=False, fill=NONE, anchor="w", padx=2, pady=4)
		self.bar = self.canvas.create_rectangle(0, 0, 1, 16, fill="#ff0000", width=0)

	def setValue(self, value):
		newValue = int(self.delta * value)
		self.canvas.coords(self.bar, 0, 0, newValue, 20)

class StatusFrame(Frame):

	def __init__(self, gui: object, app: object, width: int, height: int = 25):
		super().__init__(gui.mainWindow, width=width, height=height, padx=0, pady=0, bg='grey')

		self.gui = gui
		self.app = app
		self.field = {}

		self.pack_propagate = False
		self.pack(side=BOTTOM, expand=False, fill=X, anchor='nw')

	# Add field to status bar
	def addLabel(self, name: str, hSize: int, value: str = "", fg='black', bg='grey'):
		field = Label(self, width=hSize, text=value, bg=bg, relief=SUNKEN)
		field.pack_propagate(False)
		field.pack(side=LEFT, expand=False, fill=NONE, anchor="w", padx=2, pady=2)
		self.field[name] = field

	def addProgressbar(self, name, length):
		self.field[name] = ProgressBar(self, length)

	def setFieldValue(self, name: str, value, fg='white', bg='grey'):
		if name not in self.field:
			return False
		else:
			if isinstance(self.field[name], Label):
				self.field[name].config(text=value, fg=fg, bg=bg)
			elif isinstance(self.field[name], ProgressBar):
				self.field[name].setValue(value)
			else:
				return False
			return True
		
class DrawFrame(Frame):

	def __init__(self, gui: object, app: object, width: int, height: int, bg='black'):
		super().__init__(gui.mainWindow, width=width, height=height, padx=0, pady=0, cursor='arrow')

		self.gui = gui
		self.app = app

		self.pack_propagate(False)
		self.pack(side=LEFT, expand=False, fill=BOTH, anchor='nw')

		# Scrollbars
		self.hScroll = Scrollbar(self, orient='horizontal')
		self.vScroll = Scrollbar(self, orient='vertical')
		self.hScroll.pack(fill=X, side=BOTTOM)
		self.vScroll.pack(fill=Y, side=RIGHT)

		# Create drawing canvas and link with scrollbars
		self.canvas = Canvas(self, width=width, height=height, bg=bg, bd=0, highlightthickness=0, scrollregion=(0, 0, width, height))
		self.hScroll.config(command=self.canvas.xview)
		self.vScroll.config(command=self.canvas.yview)
		self.canvas.config(xscrollcommand=self.hScroll.set, yscrollcommand=self.vScroll.set)
		self.canvas.pack(side=LEFT, expand=False, fill=NONE, anchor='nw')

	def clearCanvas(self):
		self.canvas.delete("all")
		self.update()


class ControlFrame(Frame):

	def __init__(self, gui: object, app: object, width: int, height: int):
		# Use ScrolledText as parent for control frame
		self.controlFrameText = ScrolledText(gui.mainWindow, state='disable')
		self.controlFrameText.pack(fill='both', expand=True)

		super().__init__(self.controlFrameText, width=width, height=height, padx=0, pady=0)

		self.gui = gui
		self.app = app

		self.pack_propagate(False)
		#self.pack(side=RIGHT, expand=False, fill=Y, anchor='ne')
		self.controlFrameText.window_create('1.0', window=self)

		# Draw and Cancel Buttons
		self.btnFrame = LabelFrame(self)
		self.btnFrame.grid(columnspan=2, column=0, row=0)
		self.btnApply  = Button(self.btnFrame, text="Apply",  width=8, state=DISABLED, command=lambda: self.app.onApply())
		self.btnDraw   = Button(self.btnFrame, text="Draw",   width=8, command=lambda: self.app.onDraw())
		self.btnCancel = Button(self.btnFrame, text="Cancel", width=8, command=lambda: self.app.onCancel())
		self.btnApply.grid(column=0, row=0, padx=5, pady=5)
		self.btnDraw.grid(column=1, row=0, padx=5, pady=5)
		self.btnCancel.grid(column=2, row=0, pady=5)

		self.row = 1

	def nextRow(self):
		return self.row

class Selection:

	NOSELECTION = 0
	POINT       = 1
	AREA        = 2
	MOVEAREA    = 3

	def __init__(self, canvas: object, color = 'red', width = 2, flipY: bool = False, keepAR: bool = True):
		self.canvas     = canvas
		self.color      = color
		self.rectWidth  = width
		self.flipY      = flipY
		self.keepAR     = keepAR
		self.selectRect = None

		self.reset()

	# Enable selection
	def enable(self, scalefactor: float = 1.0):
		self.scaleFactor = scalefactor
		self.canvas.config(cursor='cross')
		self.enabled = True
	
	# Disable selection
	def disable(self):
		self.scaleFactor = 1.0
		self.canvas.config(cursor='arrow')
		self.enabled = False

	# Reset everything, selection is disabled
	def reset(self, enabled: bool = False):
		if self.selectRect is not None:
			self.canvas.delete(self.selectRect)
			self.selectRect = None
		
		if not enabled:
			self.disable()

		self.mode = Selection.NOSELECTION
		self.selected = False
		self.active   = False
		self.xs = self.ys = self.xe = self.ye = 0

	# Scale coordinates
	def scale(self, x: int, y: int) -> tuple[int]:
		return int(x / self.scaleFactor), int(y / self.scaleFactor)
	
	# Return selected point
	def getPoint(self) -> tuple[int, int]:
		self.width  = self.canvas.winfo_reqwidth()
		self.height = self.canvas.winfo_reqheight()

		if self.flipY:
			return self.scale(self.xs, self.height-self.ys-1)
		else:
			return self.scale(self.xs, self.ys)
	
	# Return selected area
	def getArea(self) -> tuple[int, int, int, int]:
		self.width  = self.canvas.winfo_reqwidth()
		self.height = self.canvas.winfo_reqheight()

		if self.flipY:
			return self.scale(self.xs, self.height-self.ye) + self.scale(self.xe, self.height-self.ys)
		else:
			return self.scale(self.xs, self.ys) + self.scale(self.xe, self.ye)
		
	# Adjust coordinates to keep aspect ratio
	def keepAspectRatio(self, xe: int, ye: int) -> tuple[int, int]:
		if self.keepAR:
			w = xe-self.xs
			h = ye-self.ys
			if abs(w) < abs(h):
				return self.xs+h, ye
			elif abs(w) > abs(h):
				return xe, self.ys+w
		return xe, ye

	# Right button click resets everything
	def onRightButtonClicked(self, event) -> bool:
		self.reset()

	# Start selection. Called when left button is pressed => point selected
	def onLeftButtonPressed(self, event) -> bool:
		if not self.enabled:
			return False
		
		x = event.x
		y = event.y

		if self.selected and (self.mode == Selection.AREA or self.mode == Selection.MOVEAREA):
			# Area selected
			if self.isInside(x, y):
				# If button pressed inside selected area, start dragging of area
				self.xo, self.yo = x, y

				self.mode     = Selection.MOVEAREA
				self.active   = True		# select mode active
				self.selected = False		# disable selection

				self.canvas.config(cursor='hand')

			else:
				# If button pressed outside selected area, cancel current selection and cleanup. Selection mode stays enabled
				self.reset(enabled=True)

		else:
			# Store start point
			self.xs, self.ys = x, y
			self.xe, self.ye = x, y

			self.mode     = Selection.POINT
			self.selected = False
			self.active   = True

			self.width  = self.canvas.winfo_reqwidth()
			self.height = self.canvas.winfo_reqheight()
			self.aspectRatio = max(self.width, self.height)/min(self.width, self.height)


		print(f"buttonPressed: mode={self.mode} selected={self.selected} active={self.active}")
		return True
	
	# Drag with mouse button pressed => select area or move selected area
	def onLeftDrag(self, event) -> bool:
		if not self.enabled:
			return False

		x = event.x
		y = event.y

		if self.mode == Selection.POINT and not self.selected:
			# Point selected, dragging from selected point => change size of area
			self.active   = True			# select mode active
			self.selected = False			# disable selection
			self.mode     = Selection.AREA	# change selection mode

			self.xe, self.ye = self.keepAspectRatio(x, y)

			# Create selection rectangle
			self.selectRect = self.canvas.create_rectangle(self.xs, self.ys, self.xe, self.ye, outline=self.color, width=self.rectWidth)

		elif self.mode == Selection.AREA and self.active:
			# Change size of selected area
			self.xe, self.ye = self.keepAspectRatio(x, y)

			# Update selection rectangle
			self.canvas.coords(self.selectRect, self.xs, self.ys, self.xe, self.ye)

		elif self.mode == Selection.MOVEAREA and self.active:
			# Move selected area, add delta x/y to previous point
			self.xs += x - self.xo
			self.ys += y - self.yo
			self.xe += x - self.xo
			self.ye += y - self.yo
			self.xo, self.yo = x, y

			# Update selection rectangle
			self.canvas.coords(self.selectRect, self.xs, self.ys, self.xe, self.ye)

		return True

	# Called when button is released
	def onLeftButtonReleased(self, event) -> bool:
		if not self.enabled:
			return False

		x = event.x
		y = event.y
		
		if self.active:
			if self.mode == Selection.AREA:
				# End of area selection, sort points => xs, ys < xe, ye
				x, y = self.keepAspectRatio(x, y)
				xs, ys = self.xs, self.ys
				self.xs = min(xs, x)
				self.ys = min(ys, y)
				self.xe = max(xs, x)
				self.ye = max(ys, y)
				self.canvas.coords(self.selectRect, self.xs, self.ys, self.xe, self.ye)

			elif self.mode == Selection.MOVEAREA:
				self.mode = Selection.AREA
				self.canvas.config(cursor='cross')

			elif self.mode != Selection.POINT:
				print(f"Invalid selection mode {self.mode} on button release")
				return False

			self.selected = True
			self.active = False
		else:
			print("Selection not active on button release")

		print(f"buttonReleased: mode={self.mode} selected={self.selected} active={self.active}")
		return True

	# Check if selection mode is enabled
	def isEnabled(self) -> bool:
		return self.enabled
	
	# Check if selection is in progress
	def isActive(self) -> bool:
		return self.active
	
	# Check if either point or area is selected
	def isSelected(self) -> bool:
		return self.selected
	
	def isPointSelected(self) -> bool:
		return self.selected and self.mode == Selection.POINT

	def isAreaSelected(self) -> bool:
		return self.selected and self.mode == Selection.AREA

	# Return selection mode (NOSELECTION, POINT, AREA)
	def mode(self) -> int:
		return self.mode
	
	# Check if point is inside the currently selected area or is matching the currently selected point
	def isInside(self, x: int, y: int) -> bool:
		if (self.mode == Selection.AREA or self.mode == Selection.MOVEAREA) and self.selected:
			return self.xs <= x <= self.xe and self.ys <= y <= self.ye
		else:
			return self.xs == x and self.ys == y
	
class GUI:

	def __init__(self, app, title: str, width: int, height: int, statusHeight: int = 50, controlWidth: int = 200):
		self.app = app

		self.width = width
		self.height = height

		# Main window
		self.mainWindow = Tk()
		self.mainWindow.title(title)
		self.mainWindow.geometry(f"{width}x{height}")

		# GUI sections
		self.statusFrame  = StatusFrame(self, self.app, width, statusHeight)
		self.drawFrame    = DrawFrame(self, self.app, width-controlWidth, height-statusHeight, bg='white')
		self.controlFrame = ControlFrame(self, self.app, controlWidth, height-statusHeight)

		# Add fields to statusframe
		self.statusFrame.addLabel('screenCoord', 25, value="0,0")
		self.statusFrame.addLabel('complexCoord', 10, value="TEXT")
		self.statusFrame.addLabel('drawing', 15, value="Idle")
		self.statusFrame.addProgressbar('progress', 100)

		# Screen selection
		self.selection = Selection(self.drawFrame.canvas, flipY=True)

		# Event handler
		self.drawFrame.canvas.bind('<Motion>',          self.onMove)
		self.drawFrame.canvas.bind('<ButtonPress-1>',   self.onLeftButtonPressed)
		self.drawFrame.canvas.bind('<B1-Motion>',       self.onLeftButtonDrag)
		self.drawFrame.canvas.bind('<ButtonRelease-1>', self.onLeftButtonReleased)
		self.drawFrame.canvas.bind('<Button-2>',        self.onRightButtonClicked)

		# Registered callback functions for selections
		self.onPoint  = None   # Point selected
		self.onArea   = None   # Area selected
		self.onCancel = None   # Selection cancelled

	def setSelectionHandler(self, onPoint = None, onArea = None, onCancel = None):
		self.onPoint  = onPoint
		self.onArea   = onArea
		self.onCancel = onCancel

	def onMove(self, event):
		if not self.selection.isActive() and not self.selection.isSelected():
			x = event.x
			y = event.y
			self.statusFrame.setFieldValue('screenCoord', f"Pos: {x},{y}", fg='white')

	def onLeftButtonPressed(self, event):
		self.selection.onLeftButtonPressed(event)

	def onLeftButtonDrag(self, event):
		if self.selection.onLeftDrag(event):
			x1, y1, x2, y2 = self.selection.getArea()
			w = x2 - x1 + 1
			h = y2 - y1 + 1
			self.statusFrame.setFieldValue('screenCoord', f"{x1},{y1} - {w}x{h}", fg='white')

	def onLeftButtonReleased(self, event):
		if self.selection.onLeftButtonReleased(event):
			if self.selection.isSelected():
				if self.selection.mode == Selection.POINT:
					x, y = self.selection.getPoint()
					self.statusFrame.setFieldValue('screenCoord', f"Point: {x},{y}", fg='white')

					if self.onPoint is not None:
						self.onPoint(x, y)
				else:
					x1, y1, x2, y2 = self.selection.getArea()
					w = x2-x1+1
					h = y2-y1+1
					self.statusFrame.setFieldValue('screenCoord', f"Area: {x1},{y1} - {x2},{y2}", fg='white')

					if self.onArea is not None:
						self.onArea(x1, y1, x2, y2)
			else:
				self.statusFrame.setFieldValue('screenCoord', "Cancelled selection")
				if self.onCancel is not None:
					self.onCancel()

	def onRightButtonClicked(self, event):
		self.statusFrame.setFieldValue('screenCoord', "Cancelled selection")
		if self.onCancel is not None:
			self.onCancel()
