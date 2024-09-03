
# PyFracExplore main

import sys

# Add path of submodule tkconfigure
sys.path.insert(0, "./src/tkconfigure/src")

from application import *

def main():
	app = Application(1200, 800, "PyFracExplore")
	app.run()

if __name__ == "__main__":
	main()
	sys.exit(0)
