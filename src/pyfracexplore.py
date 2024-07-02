
# PyFracExplore main

import sys

from application import *

def main():
	app = Application(1000, 800, "PyFracExplore")
	app.run()

if __name__ == "__main__":
	sys.exit(main())