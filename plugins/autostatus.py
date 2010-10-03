# coding: utf-8

# autostatus.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def startStatusTimer():
	hour = time.localtime()[3]
	if(hour >= 18):
		show = "chat"
	elif(hour >= 8):
		show = "dnd"
	elif(hour >= 0):
		show = "xa"
	gClient.setStatus(show, None, gPriority)
	timeout = 3600 + random.randrange(-800, 801)
	startTimer(timeout, startStatusTimer)

registerEvent(startStatusTimer, INIT_2)
