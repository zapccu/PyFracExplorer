
# PyFracExplore main

import sys
from tkinter import *
from gui import *
from graphics import *
from fractal import *
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
		self.statusFrame = StatusFrame(self.mainWindow, width, 50)
		self.drawFrame = DrawFrame(self.mainWindow, width-200, height-50, bg='white')
		self.controlFrame = ControlFrame(self, self.mainWindow, 200, height-50)
		self.statusFrame.addField(10, value="Status")
		self.statusFrame.addField(10, value="TEXT")

		# Initialize graphics
		self.graphics = Graphics(self.drawFrame, flipY=True)

	def run(self):
		self.mainWindow.mainloop()

	def onDraw(self):
		palette = ColorTable()
		palette.createLinearTable(100, Color(0, 0, 0), Color(255, 255, 255))
		# self.graphics.drawPalette()

		frc = Mandelbrot(complex(-2.0, -1.5), complex(3.0, 3.0))
		draw = Drawer(self.graphics, frc)
		draw.setPalette(palette)

		draw.drawFractal(0, 0, 800, 800, Drawer.DRAW_METHOD_RECT)

		"""
		draw.graphics.beginDraw(800, 800)
		draw.graphics.setColor(intColor = 0)

		print("Draw top and bottom")
		draw.graphics.moveTo(0, 0)
		draw.graphics.horzLineTo(800)
		draw.graphics.moveTo(0, 799)
		draw.graphics.horzLineTo(800)

		print("Draw left and right")
		draw.graphics.moveTo(0, 0)
		draw.graphics.vertLineTo(800)
		draw.graphics.moveTo(799, 0)
		draw.graphics.vertLineTo(800)

		print("Draw outline")
		draw.graphics.moveTo(0, 50)
		draw.graphics.horzLineTo(50)
		draw.graphics.moveTo(50, 0)
		draw.graphics.vertLineTo(51)

		print("Draw rectangle")
		draw.graphics.setColor(strColor = '#ff0000')
		draw.graphics.fillRect(1, 1, 50, 50)
		"""

		# draw.drawFractal(0, 0, 400, 400, Drawer.DRAW_METHOD_LINE)


def main():
	app = Application(1000, 800, "PyFracExplore")
	app.run()

if __name__ == "__main__":
	sys.exit(main())