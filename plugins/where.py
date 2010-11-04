# coding: utf-8

# where.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showWhereIsBot(msgType, conference, nick, param):
	confCount = len(getConferences())
	if confCount:
		message = u"Я сижу в %d конференциях:\n" % (confCount)
		infoList = [u"%d) %s\n[%s, %d чел.]" % (i + 1, conf, getBotNick(conf), len(getJidList(conf)))
					for i, conf in enumerate(getConferences())]
		message += "\n".join(infoList)
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"Я пока нигде не сижу")

registerCommand(showWhereIsBot, u"хдебот", 10, 
				u"Показывает, в каких конфах сидит бот", 
				None, 
				(u"хдебот", ), 
				ANY | NONPARAM)
