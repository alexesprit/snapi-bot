# coding: utf-8

# gc.py
# Garbage cleaner
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import gc

COLLECT_TIMEOUT = 300
		
def startCollecting():
	sys.exc_clear()
	gc.collect()
	startTimer(COLLECT_TIMEOUT, startCollecting)

registerEvent(startCollecting, INIT_2)
