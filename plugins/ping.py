# coding: utf-8;

# ping.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) Gigabyte

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

PING_ID = 'ping_id';

def _showPing(stanza, pingID, t0, type, conference, nick, param):
	if(pingID == stanza.getID()):
		if(RESULT == stanza.getType()):	
			ping = time.time() - t0;
			if(param):
				message = random.choice((u'понг от %s составляет', u'скорость отклика сервера для %s равна', u'скорость отправки пакетов от %s составляет', u'опа! что я откопала! это же понг от %s:', )) % (param);  
			else:
				message = random.choice((u'твой понг составляет', u'скорость отклика сервера для тебя равна', u'скорость отправки твоих пакетов', u'опа! что я откопала! это же твой понг:', ));
			message += u' %s сек.' % (str(round(ping , 2)));
			sendMsg(type, conference, nick, message);
		else:
			sendMsg(type, conference, nick, u'не пингуется :(');

def showPing(type, conference, nick, param):
	if(param):
		if(chatInList(conference) and nickOnlineInChat(conference, param)):
			userJid = conference + '/' + param;
		else:
			return;
	else:
		userJid = conference + '/' + nick;
	iq = xmpp.Iq('get');
	iq.addChild('ping', {}, [], xmpp.NS_PING);
	iq.setTo(userJid);
	pingID = getUniqueID(PING_ID);
	iq.setID(pingID);
	t0 = time.time();
	gClient.SendAndCallForResponse(iq, _showPing, (pingID, t0, type, conference, nick, param, ));

registerCommandHandler(showPing, u'пинг', 10, u'Пингует тебя или определённый ник', u'пинг [ник]', (u'пинг', u'пинг Nick'));
