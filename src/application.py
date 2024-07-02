
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
		self.statusFrame.addField('screenCoord', 10, value="0,0")
		self.statusFrame.addField('complexCoord', 10, value="TEXT")

		# Initialize graphics
		self.graphics = Graphics(self.drawFrame, flipY=True)

	def run(self):
		self.mainWindow.mainloop()

	def onMove(self, event):
		x = event.x
		y = event.y
		self.statusFrame.setFieldValue('screenCoord', f"{x},{y}", fg='white')

	def onButtonPressed(self, event):
		self.xs = event.x
		self.ys = event.y
		self.xe = event.x
		self.ye = event.y
		self.selection = self.drawFrame.canvas.create_rectangle(self.xs, self.ys, self.xe, self.ye, outline='red', width=2)

	def onDrag(self, event):
		self.xe = event.x
		self.ye = event.y
		self.drawFrame.canvas.coords(self.selection, self.xs, self.ys, self.xe, self.ye)
		self.mainWindow.update_idletasks()

	def onButtonReleased(self, event):
		self.xe = event.x
		self.ye = event.y
		self.drawFrame.canvas.delete(self.selection)	

	def onDraw(self):
		palette = ColorTable()
		palette.createLinearTable(100, Color(0, 0, 0), Color(255, 255, 255))
		# self.graphics.drawPalette()

		frc = Mandelbrot(complex(-2.0, -1.5), complex(3.0, 3.0))
		draw = Drawer(self.graphics, frc, 800, 800)
		draw.setPalette(palette)

		draw.drawFractal(0, 0, 800, 800, Drawer.DRAW_METHOD_RECT)
		# draw.drawFractal(0, 0, 800, 800, Drawer.DRAW_METHOD_LINE)
