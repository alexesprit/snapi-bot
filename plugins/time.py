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

def showUserTime(type, conference, nick, param):
	if(param):
		if(conferenceInList(conference) and nickIsOnline(conference, param)):
			userJid = conference + '/' + param;
		else:
			return;
	else:
		userJid = conference + '/' + nick;
	iq = xmpp.Iq('get');
	iq.addChild('time', {}, [], xmpp.NS_ENTITY_TIME);
	iq.setTo(userJid);
	timeID = getUniqueID(TIME_ID);
	iq.setID(timeID);
	gClient.SendAndCallForResponse(iq, _showUserTime, (timeID, type, conference, nick, param));

def _showUserTime(stanza, timeID, type, conference, nick, param):
	if(timeID == stanza.getID()):
		if(stanza.getType() == 'result'):
			tzo, utc = '', '' ;
			for p in stanza.getChildren():
				tzo = p.getTagData('tzo');
				utc = p.getTagData('utc');
			if(tzo and utc):
				sign, tzHour, tzMin = re.match('(\+|-)?([0-9]+):([0-9]+)', tzo).groups();
				year, month, day, hours, minutes, seconds = re.match('([0-9]+)-([0-9]+)-([0-9]+)T([0-9]+):([0-9]+):([0-9]+)', utc).groups();

				tzHour, tzMin = int(tzHour), int(tzMin);
				hours, minutes, seconds = int(hours), int(minutes), int(seconds);
				year, month, day = int(year), int(month), int(day);

				if(sign == '-'):
					tzHour = -tzHour;
					tzMin = -tzMin;
				hours = hours + tzHour;
				minutes = minutes + tzMin;
				while(hours >= 24):
					day += 1;
					hours -= 24;
				while(minutes >= 60):
					minutes -= 60;

				time = '%02d:%02d:%02d' % (hours, minutes, seconds);
				date = '%02d.%02d.%02d' % (day, month, year);
				if(param):
					sendMsg(type, conference, nick, u'у %s сейчас %s (%s)' % (param, time, date));
				else:
					sendMsg(type, conference, nick, u'у тебя сейчас %s (%s)' % (time, date));
			else:
				sendMsg(type, conference, nick, u'твой клиент - глюк, инфы не хватает');
		elif(stanza.getType() == 'error'):
			if(not param):
				sendMsg(type, conference, nick, u'хехе, твой клиент не дружит с этим');
			else:
				sendMsg(type, conference, nick, u'хехе, его клиент не дружит с этим');

registerCommand(showUserTime, u'часики', 10, u'Показывает время указанного пользователя', u'часики [ник]', (u'часики', u'часики Nick'));
