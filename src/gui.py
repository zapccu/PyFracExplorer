
from tkinter import *


class StatusFrame(Frame):

	def __init__(self, gui: object, app: object, width: int, height: int = 50):
		super().__init__(gui.mainWindow, width=width, height=height, padx=0, pady=0, bg='grey')

		self.gui = gui
		self.app = app
		self.field = {}

		self.pack_propagate = False
		self.pack(side=BOTTOM, expand=False, fill=X, anchor='nw')
	
	# Add field to status bar
	def addField(self, name: str, hSize: int, value: str = "", fg='black', bg='grey'):
		field = Label(self, width=hSize, text=value, bg=bg, relief=SUNKEN)
		field.pack_propagate(False)
		field.pack(side=LEFT, expand=False, fill=NONE, anchor="w", padx=2, pady=2)
		self.field[name] = field
	
	def setFieldValue(self, name: str, value: str, fg='black', bg='grey'):
		if name not in self.field:
			return False
		else:
			self.field[name].config(text=value, fg=fg, bg=bg)
			return True
		
class DrawFrame(Frame):

	def __init__(self, gui: object, app: object, width: int, height: int, bg='black'):
		super().__init__(gui.mainWindow, width=width, height=height, padx=0, pady=0, cursor='cross')

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

class ControlFrame(Frame):

	def __init__(self, gui: object, app: object, width: int, height: int, bg='grey'):
		super().__init__(gui.mainWindow, width=width, height=height, padx=0, pady=0, bg='blue')

		self.gui = gui
		self.app = app

		self.pack_propagate(False)
		self.pack(side=LEFT, expand=False, fill=Y, anchor='nw')

		self.btnDraw = Button(
            self,
            text="Draw",
            width=8,
            fg="green",
            command=lambda: self.app.onDraw(),
        ).pack()


class Selection:

	NOSELECTION = 0
	POINT       = 1
	AREA        = 2
	MOVEAREA    = 3

	def __init__(self, canvas: object, color = 'red', width = 2, flipY: bool = False, onPoint = None, onArea = None):
		self.canvas    = canvas
		self.color     = color
		self.rectWidth = width
		self.mode      = Selection.NOSELECTION
		self.flipY     = flipY

		self.onPoint = onPoint
		self.onArea  = onArea

		self.selected = False
		self.active   = False

		self.xs = self.ys = self.xe = self.ye = 0

	def getPoint(self):
		self.width     = self.canvas.winfo_reqwidth()
		self.height    = self.canvas.winfo_reqheight()
		print(f"getPoint {self.width},{self.height}")

		if self.flipY:
			return self.xs, self.height-self.ys-1
		else:
			return self.xs, self.ys
	
	def getArea(self):
		self.width     = self.canvas.winfo_reqwidth()
		self.height    = self.canvas.winfo_reqheight()

		if self.flipY:
			return self.xs, self.height-self.ye, self.xe, self.height-self.ys
		else:
			return self.xs, self.ys, self.xe, self.ye
	
	# Start selection. Called when button is pressed => point selected
	def onLeftButtonPressed(self, event):
		x = event.x
		y = event.y

		if self.selected and (self.mode == Selection.AREA or self.mode == Selection.MOVEAREA):
			# Area selected
			if self.isInside(x, y):
				# If button pressed inside selected area, start dragging of area
				self.xo, self.yo = x, y

				self.mode     = Selection.MOVEAREA
				self.active   = True	# select mode active
				self.selected = False	# disable selection

				self.canvas.config(cursor='hand')

			else:
				# If button pressed outside selected area, cancel selection and cleanup
				self.xs = self.ys = self.xe = self.ye = 0

				self.mode     = Selection.NOSELECTION
				self.selected = False
				self.active   = False

				# Delete rectangle
				if self.mode == Selection.AREA or self.mode == Selection.MOVEAREA:
					self.canvas.delete(self.selectRect)

		else:
			# Store start point
			self.xs, self.ys = x, y
			self.xe, self.ye = x, y

			self.mode     = Selection.POINT
			self.selected = False
			self.active   = True

		print(f"buttonPressed: mode={self.mode} selected={self.selected} active={self.active}")
	
	# Drag with mouse button pressed => select area or move selected area
	def onLeftDrag(self, event):
		x = event.x
		y = event.y

		if self.mode == Selection.POINT and not self.selected:
			# Point selected, dragging from selected point => change size of area
			self.active   = True			# select mode active
			self.selected = False			# disable selection
			self.mode     = Selection.AREA	# change selection mode
			self.xe, self.ye = x, y

			# Create selection rectangle
			self.selectRect = self.canvas.create_rectangle(self.xs, self.ys, self.xe, self.ye, outline=self.color, width=self.width)

		elif self.mode == Selection.AREA and self.active:
			# Change size of selected area
			self.xe, self.ye = x, y

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

	# Called when button is released
	def onLeftButtonReleased(self, event):
		x = event.x
		y = event.y
		
		if self.active:
			if self.mode == Selection.POINT:
				self.selected = True
				self.active   = False

			elif self.mode == Selection.AREA or self.mode == Selection.MOVEAREA:
				if self.mode == Selection.AREA:
					# End of area selection, sort points => xs, ys < xe, ye
					xs, ys = self.xs, self.ys
					self.xs = min(xs, x)
					self.ys = min(ys, y)
					self.xe = max(xs, x)
					self.ye = max(ys, y)
					self.canvas.coords(self.selectRect, self.xs, self.ys, self.xe, self.ye)

				self.active = False
				self.selected = True
				self.canvas.config(cursor='cross')

		print(f"buttonReleased: mode={self.mode} selected={self.selected} active={self.active}")

	def isActive(self):
		return self.active
	
	def isSelected(self):
		return self.selected
	
	def isInside(self, x: int, y: int) -> bool:
		if (self.mode == Selection.AREA or self.mode == Selection.MOVEAREA) and self.selected:
			return self.xs <= x <= self.xe and self.ys <= y <= self.ye
		else:
			return self.xs == x and self.ys == y
	
class GUI:

	def __init__(self, app, title: str, width: int, height: int):
		self.app = app

		self.width = width
		self.height = height

		# Main window
		self.mainWindow = Tk()
		self.mainWindow.title(title)
		self.mainWindow.geometry(f"{width}x{height}")

		# GUI sections
		self.statusFrame  = StatusFrame(self, self.app, width, 50)
		self.drawFrame    = DrawFrame(self, self.app, width-200, height-50, bg='white')
		self.controlFrame = ControlFrame(self, self.app, 200, height-50)

		# Add fields to statusframe
		self.statusFrame.addField('screenCoord', 25, value="0,0")
		self.statusFrame.addField('complexCoord', 10, value="TEXT")

		# Screen selection
		self.selection = Selection(self.drawFrame.canvas, flipY=True)

		# Event handler
		self.drawFrame.canvas.bind('<Motion>',          self.onMove)
		self.drawFrame.canvas.bind('<ButtonPress-1>',   self.onLeftButtonPressed)
		self.drawFrame.canvas.bind('<B1-Motion>',       self.onLeftButtonDrag)
		self.drawFrame.canvas.bind('<ButtonRelease-1>', self.onLeftButtonReleased)

		# Selection handler
		self.onPoint = None
		self.onArea = None

	def setSelectionHandler(self, onPoint = None, onArea = None):
		self.onPoint = onPoint
		self.onArea  = onArea

	def onMove(self, event):
		if not self.selection.isActive():
			x = event.x
			y = event.y
			self.statusFrame.setFieldValue('screenCoord', f"{x},{y}", fg='white')

	def onLeftButtonPressed(self, event):
		self.selection.onLeftButtonPressed(event)

	def onLeftButtonDrag(self, event):
		self.selection.onLeftDrag(event)
		x1, y1, x2, y2 = self.selection.getArea()
		w = x2 - x1 + 1
		h = y2 - y1 + 1
		self.statusFrame.setFieldValue('screenCoord', f"{x1},{y1} - {w} x {h}", fg='white')

	def onLeftButtonReleased(self, event):
		self.selection.onLeftButtonReleased(event)

		if self.selection.isSelected():
			if self.selection.mode == Selection.POINT:
				x, y = self.selection.getPoint()
				self.statusFrame.setFieldValue('screenCoord', f"{x},{y}", fg='white')

				if self.onPoint is not None:
					print("Calling onPoint")
					self.onPoint(x, y)
			else:
				x1, y1, x2, y2 = self.selection.getArea()
				w = x2-x1+1
				h = y2-y1+1
				# c = self.fractal.mapXY(x1, y1)
				# s = self.fractal.mapWH(x2-x1+1, y2-y1+1)
				# print(f"c={c}, s={s}")
				self.statusFrame.setFieldValue('screenCoord', f"{x1},{y1} - {x2},{y2}", fg='white')

				if self.onArea is not None:
					print("Calling onArea")
					self.onArea(x1, y1, x2, y2)
		else:
			self.statusFrame.setFieldValue('screenCoord', "Cancelled selection")