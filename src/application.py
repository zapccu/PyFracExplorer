
from tkinter import *
from gui import *
from drawer import *

class Application:

	width = 800
	height = 800

	def __init__(self, width: int, height: int, title: str):
		self.width = width
		self.height = height

		# Main window
		self.mainWindow = Tk()
		self.mainWindow.title(title)
		self.mainWindow.geometry(f"{width}x{height}")

		# GUI sections
		self.statusFrame = StatusFrame(self, width, 50)
		self.drawFrame = DrawFrame(self, width-200, height-50, bg='white')
		self.controlFrame = ControlFrame(self, 200, height-50)
		self.statusFrame.addField('screenCoord', 25, value="0,0")
		self.statusFrame.addField('complexCoord', 10, value="TEXT")

		# Initialize graphics
		self.graphics = Graphics(self.drawFrame, flipY=True, inMemory=True)

		# Screen selection
		self.selection  = Selection(self.drawFrame.canvas)

	def run(self):
		self.mainWindow.mainloop()

	#
	# Screen selection handling
	# 

	def onMove(self, event):
		x = event.x
		y = event.y
		self.statusFrame.setFieldValue('screenCoord', f"{x},{y}", fg='white')

	def onLeftButtonPressed(self, event):
		self.selection.buttonPressed(event.x, event.y)

	def onLeftDrag(self, event):
		self.selection.drag (event.x, event.y)
		x1, y1, x2, y2 = self.selection.getArea()
		self.statusFrame.setFieldValue('screenCoord', f"{x1},{y1} - {x2},{y2}", fg='white')

	def onLeftButtonReleased(self, event):
		self.selection.buttonReleased(event.x, event.y)
		if self.selection.isSelected():
			if self.selection.mode == Selection.POINT:
				x, y = self.selection.getPoint()
				self.statusFrame.setFieldValue('screenCoord', f"Selection: {x},{y}", fg='white')
			else:
				x1, y1, x2, y2 = self.selection.getArea()
				self.statusFrame.setFieldValue('screenCoord', f"Selection: {x1},{y1} - {x2},{y2}", fg='white')
		else:
			self.statusFrame.setFieldValue('screenCoord', "Cancelled selection")

	#
	# Command handling
	#
	
	def onDraw(self):
		palette = ColorTable()
		palette.createLinearTable(100, Color(0, 0, 0), Color(255, 255, 255))

		frc = Mandelbrot(complex(-2.0, -1.5), complex(3.0, 3.0))
		draw = Drawer(self.graphics, frc, 800, 800)
		draw.setPalette(palette)

		draw.drawFractal(0, 0, 800, 800, Drawer.DRAW_METHOD_RECT)
		# draw.drawFractal(0, 0, 800, 800, Drawer.DRAW_METHOD_LINE)
