# coding: utf-8;

# status.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showUserStatus(type, conference, nick, param):
	userNick = param or nick;
	if(nickIsOnline(conference, userNick)):
		show = getNickKey(conference, userNick, NICK_SHOW);
		status = getNickKey(conference, userNick, NICK_STATUS);
		if(param):
			if(status):
				sendMsg(type, conference, nick, u'%s сейчас %s (%s)' % (userNick, show, status));
			else:
				sendMsg(type, conference, nick, u'%s сейчас %s' % (userNick, show));
		else:
			if(status):
				sendMsg(type, conference, nick, u'ты сейчас %s (%s)' % (show, status));
			else:
				sendMsg(type, conference, nick, u'ты сейчас %s' % (show));
	else:
		sendMsg(type, conference, nick, u'а это кто?');
				
registerCommand(showUserStatus, u'статус', 10, u'Показывает статус указанного пользователя', u'статус [ник]', (u'статус', u'статус Nick'), CHAT);

def updateStatus(stanza, conference, nick, trueJid):
	if(conferenceInList(conference) and nickIsOnline(conference, nick)):
		show = stanza.getShow();
		status = stanza.getStatus();
		setNickKey(conference, nick, NICK_SHOW, show or u'online');
		if(status):
			setNickKey(conference, nick, NICK_STATUS, status);

registerPresenceHandler(updateStatus, CHAT);
