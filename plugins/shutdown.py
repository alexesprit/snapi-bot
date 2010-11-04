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
	nick = (conferenceInList(conference)) and nick or conference.split("@")[0]
	if param:
		message = u"Меня перезагружает %s (%s)" % (nick, param)
	else:
		message = u"Меня перезагружает %s" % (nick)
	prs = protocol.Presence(typ=protocol.PRS_OFFLINE)
	prs.setStatus(message)
	gClient.send(prs)
	shutdown(True)

def botShutdown(msgType, conference, nick, param):
	nick = (conferenceInList(conference)) and nick or conference.split("@")[0]
	if param:
		message = u"Меня выключает %s (%s)" % (nick, param)
	else:
		message = u"Меня выключает %s" % (nick)
	prs = protocol.Presence(typ=protocol.PRS_OFFLINE)
	prs.setStatus(message)
	gClient.send(prs)
	shutdown()

registerCommand(botRestart, u"рестарт", 100, 
				u"Перезапускает бота", 
				u"рестарт [причина]", 
				(u"рестарт", u"рестарт ы!"), 
				ANY | FROZEN)
registerCommand(botShutdown, u"идиспать", 100, 
				u"Остановка и полный выход бота", 
				u"идиспать [причина]", 
				(u"идиспать", u"идиспать обновления!11"), 
				ANY | FROZEN)
