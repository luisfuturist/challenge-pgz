import sys

import pgzrun

# This will set the arguments so pgzrun knows what to run
sys.argv = ["pgzrun", "game.py"]

pgzrun.go()
