# coding: utf-8;

# time.py
# Initial Copyright (с) 2007 Als <Als@exploit.in>
# Modification Copyright (с) 2007 dimichxp <dimichxp@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

TIME_ID = 'time_id';

def showUserTime(msgType, conference, nick, param):
	if(param):
		if(conferenceInList(conference) and nickIsOnline(conference, param)):
			userJid = conference + '/' + param;
		else:
			sendMsg(msgType, conference, nick, u'а это кто?');
			return;
	else:
		userJid = conference + '/' + nick;
	iq = xmpp.Iq(xmpp.TYPE_GET);
	iq.addChild('time', {}, [], xmpp.NS_ENTITY_TIME);
	iq.setTo(userJid);
	iq.setID(getUniqueID(TIME_ID));
	gClient.SendAndCallForResponse(iq, _showUserTime, (msgType, conference, nick, param));

def _showUserTime(stanza, msgType, conference, nick, param):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		tzo, utc = None, None;
		for p in stanza.getChildren():
			tzo = p.getTagData('tzo');
			utc = p.getTagData('utc');
		if(tzo and utc):
			sign, tzHour, tzMin = re.match('(\+|-)?([0-9]+):([0-9]+)', tzo).groups();
			offset = int(tzHour) * 3600 + int(tzMin) * 60;
			if(sign == "-"):
				offset = -offset;
			rawTime = time.strptime(utc, "%Y-%m-%dT%H:%M:%SZ");
			rawTime = time.mktime(rawTime) + offset;
			userTime = time.strftime("%H:%M:%S (%d.%m.%y)", time.localtime(rawTime));
			if(param):
				sendMsg(msgType, conference, nick, u'у %s сейчас %s' % (param, userTime));
			else:
				sendMsg(msgType, conference, nick, u'у тебя сейчас %s' % (userTime));
		else:
			sendMsg(msgType, conference, nick, u'клиент глюк, инфы не хватает');
	else:
		if(not param):
			sendMsg(msgType, conference, nick, u'хехе, твой клиент не дружит с этим');
		else:
			sendMsg(msgType, conference, nick, u'хехе, клиент у %s не дружит с этим' % (param));

registerCommand(showUserTime, u'часики', 10, u'Показывает время указанного пользователя', u'часики [ник]', (u'часики', u'часики Nick'));
