# coding: utf-8;

# servers.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Initial Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

INFO_ID = 'info_id';
STATS_ID = 'stats_id';
UPTIME_ID = 'uptime_id';

def _showServerStats(stanza, msgType, conference, nick, param):
	if(STATS_ID == stanza.getID()):
		if(RESULT == stanza.getType()):
			message = u'Инфа о %s:' % param;
			for stat in stanza.getQueryPayload():
				attr = stat.getAttrs();
				message += u'\n%s: %s %s' % (attr['name'], attr['value'], attr['units']);
			sendMsg(msgType, conference, nick, message);
		else:
			sendMsg(msgType, conference, nick, u'не получается :(');

def _showServerInfo(stanza, msgType, conference, nick, param):
	if(INFO_ID == stanza.getID()):
		if(RESULT == stanza.getType()):
			iq = xmpp.Iq('get', xmpp.NS_STATS);
			iq.setQueryPayload(stanza.getQueryChildren());
			iq.setTo(param);
			iq.setID(STATS_ID);
			gClient.SendAndCallForResponse(iq, _showServerStats, (msgType, conference, nick, param, ));
		else:
			sendMsg(msgType, conference, nick, u'не получается :(');

def showServerInfo(msgType, conference, nick, param):
	param = param or gHost;
	iq = xmpp.Iq('get', xmpp.NS_STATS);
	iq.setTo(param);
	iq.setID(INFO_ID);
	gClient.SendAndCallForResponse(iq, _showServerInfo, (msgType, conference, nick, param, ));

def _showServerUptime(stanza, msgType, conference, nick, param):
	if(UPTIME_ID == stanza.getID()):
		if(RESULT == stanza.getType()):
			for p in stanza.getPayload():
				sec = p.getAttrs()['seconds'];
				if(not sec == '0'):
					sendMsg(msgType, conference, nick, u'%s работает уже %s' % (param, time2str(int(sec))));
					break;
		elif(stanza.getType() == 'error'):
			sendMsg(msgType, conference, nick, u'не получается :(');

def showServerUptime(msgType, conference, nick, param):
	param = param or gHost;
	iq = xmpp.Iq('get', xmpp.NS_LAST);
	iq.setTo(param);
	iq.setID(UPTIME_ID);
	gClient.SendAndCallForResponse(iq, _showServerUptime, (msgType, conference, nick, param, ));

registerCommand(showServerInfo, u'инфа', 10, u'Возвращает статистику о сервере', u'инфа [сервер]', (u'инфа jabber.aq', ));
registerCommand(showServerUptime, u'аптайм', 10, u'Показывает аптайм определённого сервера', u'аптайм [сервер]', (u'аптайм freize.org', ));
