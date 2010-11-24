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
	conferences = getConferences()
	if conferences:
		items = [u"%d) %s [%d]" % (i + 1, conf, len(getOnlineNicks(conf)))
					for i, conf in enumerate(sorted(conferences))]
		message = u"Я нахожусь в %d конференциях:\n%s" % (len(conferences), "\n".join(items))
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"Сейчас меня нет ни в одной конференции")

registerCommand(showWhereIsBot, u"хдебот", 10, 
				u"Показывает список конференций, в которых находится бот", 
				None, 
				None, 
				CMD_ANY | CMD_NONPARAM)
