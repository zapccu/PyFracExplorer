
###############################################################################
#
#  PyFracExplore
#
#  Mandelbrot and Julia set demo program
#
#  Written 2024 by Dirk Braner
#
#  Github: https://github.com/zapccu/PyFracExplorer
#
###############################################################################

import sys

# Add path of submodule tkconfigure
# sys.path.insert(0, "./src/tkconfigure/src") 

from application import *

def main():
	app = Application(1400, 900, "PyFracExplore")
	app.run()

if __name__ == "__main__":
	main()
	sys.exit(0)
