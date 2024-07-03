
from tkinter import *

class StatusFrame(Frame):

	def __init__(self, app: object, width: int, height: int = 50):
		super().__init__(app.mainWindow, width=width, height=height, padx=0, pady=0, bg='grey')

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

	def __init__(self, app: object, width: int, height: int, bg='black'):
		super().__init__(app.mainWindow, width=width, height=height, padx=0, pady=0, cursor='cross')

		self.app = app

		self.pack_propagate(False)
		self.pack(side=LEFT, expand=False, fill=BOTH, anchor='nw')

		# Scrollbars
		self.hScroll = Scrollbar(self, orient='horizontal')
		self.vScroll = Scrollbar(self, orient='vertical')
		self.hScroll.pack(fill=X, side=BOTTOM)
		self.vScroll.pack(fill=Y, side=RIGHT)

		self.canvas = Canvas(self, width=width, height=height, bg=bg, bd=0, scrollregion=(0, 0, width, height))
		self.canvasWidth = width
		self.canvasHeight = height

		self.hScroll.config(command=self.canvas.xview)
		self.vScroll.config(command=self.canvas.yview)

		self.canvas.config(xscrollcommand=self.hScroll.set, yscrollcommand=self.vScroll.set)
		self.canvas.pack(side=LEFT, expand=False, fill=NONE, anchor='nw')

		# Event handler
		self.canvas.bind('<Motion>', self.app.onMove)
		self.canvas.bind('<ButtonPress-1>', self.app.onLeftButtonPressed)
		self.canvas.bind('<B1-Motion>', self.app.onLeftDrag)
		self.canvas.bind('<ButtonRelease-1>', self.app.onLeftButtonReleased)

	def setCanvasRes(self, width: int, height: int):
		if width != self.canvasWidth or height != self.canvasHeight:
			self.canvas.configure(width=width, height=height, scrollregion=(0, 0, width, height))
			self.canvasWidth = width
			self.canvasHeight = height

class ControlFrame(Frame):

	def __init__(self, app: object, width: int, height: int, bg='grey'):
		super().__init__(app.mainWindow, width=width, height=height, padx=0, pady=0, bg='blue')

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

	POINT = 0
	AREA = 1

	def __init__(self, canvas):
		self.canvas = canvas
		self.mode = Selection.POINT
		self.selected = False
		self.active = False
		self.moving = False
		self.xs = 0
		self.ys = 0
		self.xe = 0
		self.ye = 0

	def getPoint(self):
		return self.xs, self.ys
	
	def getArea(self):
		return self.xs, self.ys, self.xe, self.ye
	
	# Start selection. Called when left button is pressed => Point selected
	def buttonPressed(self, x: int, y: int):
		if self.selected and self.mode == Selection.AREA:
			if self.isInside(x, y):
				self.grab(x, y)
			else:
				self.clear()
		else:
			self.xs = x
			self.ys = y
			self.xe = x
			self.ye = y
			self.mode = Selection.POINT
			self.selected = True
			self.active = False
			self.moving = False

	# Grab a selected area. Called when left button is pressed inside 
	def grab(self, x: int, y: int):
		if self.mode == Selection.AREA:
			self.xo = x
			self.yo = y 
			self.active = True
			self.moving = True
			self.selected = False
	
	def drag(self, x, y):
		if self.mode == Selection.POINT and self.selected:
			self.active = True
			self.selected = False
			self.mode = Selection.AREA
			self.xe = x
			self.ye = y
			self.selection = self.canvas.create_rectangle(self.xs, self.ys, self.xe, self.ye, outline='red', width=2)
		elif self.mode == Selection.AREA and self.active:
			if self.moving:
				self.xs += x - self.xo
				self.ys += y - self.yo
				self.xe += x - self.xo
				self.ye += y - self.yo
				self.xo = x
				self.yo = y
			else:
				self.xe = x
				self.ye = y
			self.canvas.coords(self.selection, self.xs, self.ys, self.xe, self.ye)

	def buttonReleased(self, x: int, y: int):
		self.xe = x
		self.ye = y
		if self.active:
			self.selected = True
		self.active = False
		self.moving = False

	def clear(self):
		self.xs = 0
		self.ys = 0
		self.xe = 0
		self.ye = 0
		self.selected = False
		self.active = False
		self.moving = False
		if self.mode ==  Selection.AREA:
			self.canvas.delete(self.selection)

	def isActive(self):
		return self.active
	
	def isMoving(self):
		return self.moving
	
	def isSelected(self):
		return self.selected
	
	def isInside(self, x: int, y: int) -> bool:
		if self.mode == Selection.AREA and self.selected:
			return self.xs <= x <= self.xe and self.ys <= y <= self.ye
		else:
			return self.xs == x and self.ys == y
	