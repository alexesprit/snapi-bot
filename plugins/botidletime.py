# coding: utf-8

# botidletime.py
# Initial Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

gBotIdleTime = {}

def initBotIdleData(conference):
	gBotIdleTime[conference] = time.time()

def freeBotIdleData(conference):
	del gBotIdleTime[conference]

def updateBotIdleTime(msgType, conference, text):
	if protocol.TYPE_PUBLIC == msgType and text:
		gBotIdleTime[conference] = time.time()

def showBotIdleTime(msgType, conference, nick, param):
	conferences = getConferences()
	if conferences:
		elements = [u"%d) %s [%s]" % 
					(i + 1, conf, getUptimeStr(time.time() - gBotIdleTime[conf]))
						for i, conf in enumerate(sorted(conferences))]
		message = u"Вот, что я знаю:\n%s" % ("\n".join(elements))
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"Сейчас меня нет ни в одной конференции")

registerEventHandler(initBotIdleData, EVT_ADDCONFERENCE)
registerEventHandler(freeBotIdleData, EVT_DELCONFERENCE)

registerEventHandler(updateBotIdleTime, EVT_SELFMSG)

registerCommand(showBotIdleTime, u"idletime", 100, 
				u"Показывает время неактивности бота в конференциях", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
