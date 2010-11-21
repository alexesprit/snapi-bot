# coding: utf-8

# roster.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showRoster(msgType, conference, nick, param):
	items = [u"%d) %s [%s]" % (i + 1, jid, gRoster.getSubscription(jid)) \
			for i, jid in enumerate(sorted(gRoster.keys()))]
	sendMsg(msgType, conference, nick,  u"Смотри, кто у меня есть:\n" + "\n".join(items))

registerCommand(showRoster, u"ростер", 100, 
				u"Показывает содержимое ростера", 
				None, 
				None, 
				CMD_ROSTER | CMD_NONPARAM)
