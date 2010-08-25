# coding: utf-8;

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

def showRoster(type, conference, nick, param):
	items = [u'%d) %s [%s]' % (i + 1, jid, gRoster.getSubscription(jid)) for i, jid in enumerate(gRoster.getItems())];
	sendMsg(type, conference, nick,  u'смотри, кто у меня есть:\n' + '\n'.join(items));

registerCommand(showRoster, u'ростер', 100, u'Показывает содержимое ростера', u'ростер', (u'ростер'), ROSTER | NONPARAM);
