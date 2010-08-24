# coding: utf-8;

# seen.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showSeenTime(type, conference, nick, param):
	userNick = param or nick;
	if(nickInChat(conference, userNick)):
		seenTime = getNickKey(conference, userNick, NICK_LEAVED);
		if(seenTime):
			seenTime = time2str(time.time() - seenTime);
			if(not param):
				sendMsg(type, conference, nick, u'я видела тебя %s назад' % (seenTime));
			else:
				sendMsg(type, conference, nick, u'я видела %s %s назад' % (userNick, seenTime));

registerCommandHandler(showSeenTime, u'когдабыл', 10, u'Показывает, сколько времени назад пользователь вышел из чата', u'когдабыл [ник]', (u'когдабыл Nick', ), CHAT);
