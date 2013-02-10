# coding: utf-8

# record.py
# Initial Copyright (с) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

REC_FILE = "record.dat"

def openRecords(conference):
	path = getConfigPath(conference, REC_FILE)
	return io.load(path, {})

def saveRecords(conference, records):
	path = getConfigPath(conference, REC_FILE)
	io.dump(path, records)
	
def showRecord(msgType, conference, nick, param):
	records = openRecords(conference)
	if records:
		sendMsg(msgType, conference, nick, 
				u"Рекорд посещаемости - %(count)d человек (%(time)s)" % (records))
	else:
		sendMsg(msgType, conference, nick, u"Нет информации")

def calculateRecord(conference, nick, truejid, aff, role):
	records = openRecords(conference)
	userCount = len(getOnlineNicks(conference))
	lastCount = records and records["count"] or 0
	if userCount >= lastCount:
		records["time"] = time.strftime("%d.%m.%Y, %H:%M")
		records["count"] = userCount
		saveRecords(conference, records)

registerEventHandler(calculateRecord, EVT_USERJOIN)

registerCommand(showRecord, u"рекорд", 10, 
				u"Показывает рекорд посещаемости конференции", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
