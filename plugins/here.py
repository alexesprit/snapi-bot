# coding: utf-8;

# here.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showHereTime(type, conference, nick, param):
	userNick = param or nick;
	if(nickIsOnline(conference, userNick)):
		joinedTime = getNickKey(conference, userNick, NICK_JOINED);
		joinedTime = time2str(time.time() - joinedTime);
		if(not param):
			sendMsg(type, conference, nick, u'ты уже здесь %s' % (joinedTime));
		else:
			sendMsg(type, conference, nick, u'%s уже здесь %s' % (userNick, joinedTime));
	else:
		sendMsg(type, conference, nick, u'а это кто?');

registerCommand(showHereTime, u'здесь', 10, u'Показывает, сколько времени пользователь сидит в конференции', u'здесь [ник]', (u'здесь', u'здесь Nick'), CHAT);
