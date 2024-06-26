
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
		self.graphics.setColorTable(palette)

		frc = Mandelbrot(complex(-2.0, -1.5), complex(3.0, 3.0))
		draw = Drawer(self.graphics, frc)
		draw.drawLineByLine(0, 0, 100, 100)


def main():
	app = Application(1000, 800, "PyFracExplore")
	app.run()

if __name__ == "__main__":
	sys.exit(main())