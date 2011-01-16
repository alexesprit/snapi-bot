# coding: utf-8

# shutdown.py
# Initial Copyright (c) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def botRestart(msgType, conference, nick, param):
	nick = (isConferenceInList(conference)) and nick or conference.split("@")[0]
	prs = protocol.Presence(typ=protocol.PRS_OFFLINE)
	if param:
		prs.setStatus(u"Меня перезагружает %s (%s)" % (nick, param))
	else:
		prs.setStatus(u"Меня перезагружает %s" % (nick))
	gClient.send(prs)
	shutdown(True)

def botShutdown(msgType, conference, nick, param):
	nick = (isConferenceInList(conference)) and nick or conference.split("@")[0]
	prs = protocol.Presence(typ=protocol.PRS_OFFLINE)
	if param:
		prs.setStatus(u"Меня выключает %s (%s)" % (nick, param))
	else:
		prs.setStatus(u"Меня выключает %s" % (nick))
	gClient.send(prs)
	shutdown()

registerCommand(botRestart, u"рестарт", 100, 
				u"Перезапускает бота", 
				u"[причина]", 
				(None, u"обновление"), 
				CMD_ANY | CMD_FROZEN)
registerCommand(botShutdown, u"идиспать", 100, 
				u"Выключает бота", 
				u"[причина]", 
				(None, u"тех. работы"), 
				CMD_ANY | CMD_FROZEN)
