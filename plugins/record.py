# coding: utf-8

# record.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

REC_FILE = "record.txt"
gRecords = {}

def loadRecordsBase(conference):
	path = getConfigPath(conference, REC_FILE)
	gRecords[conference] = eval(utils.readFile(path, "{}"))

def freeRecordsBase(conference):
	del gRecords[conference]

def showRecord(msgType, conference, nick, param):
	if gRecords[conference]:
		sendMsg(msgType, conference, nick, 
				u"Рекорд посещаемости - %(count)d человек (%(time)s)" % (gRecords[conference]))
	else:
		sendMsg(msgType, conference, nick, u"Нет информации")
		
def calculateRecord(conference, nick, truejid, aff, role):
	userCount = len(getOnlineNicks(conference))
	lastCount = gRecords[conference] and gRecords[conference]["count"] or 0
	if userCount >= lastCount:
		gRecords[conference]["time"] = time.strftime("%d.%m.%y, %H:%M")
		gRecords[conference]["count"] = userCount
		path = getConfigPath(conference, REC_FILE)
		utils.writeFile(path, str(gRecords[conference]))
	
registerEventHandler(calculateRecord, EVT_USERJOIN)

registerEventHandler(loadRecordsBase, EVT_ADDCONFERENCE)
registerEventHandler(freeRecordsBase, EVT_DELCONFERENCE)

registerCommand(showRecord, u"рекорд", 10, 
				u"Показывает рекорд посещаемости конференции", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
