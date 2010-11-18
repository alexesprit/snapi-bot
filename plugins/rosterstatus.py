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

ROSTERSTATUS_FILE = "rosterstatus.txt"

gRosterStatus = {}

def loadRosterStatusValue():
	global gRosterStatus
	path = getConfigPath(ROSTERSTATUS_FILE)
	utils.createFile(path, "{}")
	gRosterStatus = eval(utils.readFile(path))

def updateRosterStatus():
	global gRosterStatus
	if gRosterStatus:
		show = gRosterStatus["show"]
		status = gRosterStatus["status"]
		gClient.setStatus(show, status, gPriority)

def setRosterStatus(msgType, conference, nick, param):
	args = param.split(None, 1)
	show, status = None, None

	if args[0] in STATUS_STRINGS:
		show = args[0]
		if len(args) > 1:
			status = args[1]
	else:
		status = param
	gClient.setStatus(show, status, gPriority)

	gRosterStatus["show"] = show
	gRosterStatus["status"] = status

	path = getConfigPath(ROSTERSTATUS_FILE)
	utils.writeFile(path, str(gRosterStatus))
	
	sendMsg(msgType, conference, nick, u"Запомнила")

registerEvent(loadRosterStatusValue, STARTUP)
registerEvent(updateRosterStatus, INIT_2)

registerCommand(setRosterStatus, u"ростерстатус", 100, 
				u"Устанавливает статус в ростере", 
				u"<[статус] [текст]>", 
				(u"away", u"away сплю"), 
				ROSTER | PARAM)

