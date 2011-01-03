# coding: utf-8

# rosterstatus.py
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

def updateRosterStatus():
	hour = time.localtime()[3]
	if hour >= 16:
		show = protocol.PRS_CHAT
	elif hour >= 8:
		show = protocol.PRS_DND
	elif hour >= 0:
		show = protocol.PRS_NA
	gClient.setStatus(show, None, gConfig.PRIORITY)
	timeout = 3600 * 8 + random.randrange(-800, 801)
	startTimer(timeout, updateRosterStatus)

registerEventHandler(updateRosterStatus, EVT_READY)
