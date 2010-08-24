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
	if(nickOnlineInChat(conference, nick)):
		statusMsg = getNickKey(conference, nick, 'stmsg');
		status = getNickKey(conference, nick, 'status');
		if(param):
			if(statusMsg):
				sendMsg(type, conference, nick, u'%s сейчас %s (%s)' % (param, status, statusMsg));
			else:
				sendMsg(type, conference, nick, u'%s сейчас %s' % (param, status));
		else:
			if(statusMsg):
				sendMsg(type, conference, nick, u'ты сейчас %s (%s)' % (status, statusMsg));
			else:
				sendMsg(type, conference, nick, u'ты сейчас %s' % (status));
				
registerCommandHandler(showUserStatus, u'статус', 10, u'Показывает статус указанного пользователя', u'статус [ник]', (u'статус', u'статус Nick'), CHAT);

def updateStatus(stanza, conference, nick, trueJid):
	if(chatInList(conference) and nickOnlineInChat(conference, nick)):
		statusMsg = stanza.getStatus();
		status = stanza.getShow();
		setNickKey(conference, nick, 'status', status or u'online');
		if(statusMsg):
			setNickKey(conference, nick, 'stmsg', statusMsg);

registerPresenceHandler(updateStatus, CHAT);
