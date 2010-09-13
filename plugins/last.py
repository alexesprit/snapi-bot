# coding: utf-8;

# last.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

LAST_ID = 'last_id';

def showOnlineTime(msgType, conference, nick, param):
	iq = xmpp.Iq('get', xmpp.NS_LAST);
	iq.setTo(conference);
	lastID = getUniqueID(LAST_ID);
	iq.setID(lastID);
	gClient.SendAndCallForResponse(iq, _showOnlineTime, (lastID, msgType, conference, nick, ));

def _showOnlineTime(stanza, lastID, msgType, conference, nick):
	if(lastID == stanza.getID()):
		if(RESULT == stanza.getType()):
			for p in stanza.getPayload():
				sec = p.getAttrs()['seconds'];
				if(not sec == '0'):
					sendMsg(msgType, conference, nick, u'ты в сети уже %s' % (time2str(int(sec))));
					break;
		else:
			sendMsg(msgType, conference, nick, u'не получается :(');

registerCommand(showOnlineTime, u'всети', 10, u'Показывает ваше время в сети', None, (u'всети', ), ROSTER | NONPARAM);
