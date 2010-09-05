# coding: utf-8;

# version.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

VER_ID = 'ver_id';

def showVersion(msgType, conference, nick, param):
	if(param == getBotNick(conference)):
		sendMsg(msgType, conference, nick, u'я юзаю %s %s в %s' % (gVersion[0], gVersion[1], gVersion[2]));
	else:
		if(param):
			if(conferenceInList(conference) and nickIsOnline(conference, param)):
				jid = conference + '/' + param;
			else:
				sendMsg(msgType, conference, nick, u'а это кто?');
				return;
		else:
			jid = conference + '/' + nick;
		iq = xmpp.Iq('get', xmpp.NS_VERSION);
		iq.setTo(jid);
		verID = getUniqueID(VER_ID);
		iq.setID(verID);
		gClient.SendAndCallForResponse(iq, _showVersion, (verID, msgType, conference, nick, param, ));

def _showVersion(stanza, verID, msgType, conference, nick, param):
	if(verID == stanza.getID()):
		if(RESULT == stanza.getType()):
			name, ver, os = '', '', '';
			for p in stanza.getQueryChildren():
				if(p.getName() == 'name'):
					name = p.getData();
				elif(p.getName() == 'version'):
					ver = p.getData();
				elif(p.getName() == 'os'):
					os = p.getData();
			version = u'';
			if(name):
				version += name;
			if(ver):
				version += u' ' + ver;
			if(os):
				version += u' в ' + os;
			if(version):
				if(not param):
					sendMsg(msgType, conference, nick, u'ты юзаешь %s' % (version));
				else:
					sendMsg(msgType, conference, nick, u'%s юзает %s' % (param, version));
			else:
				sendMsg(msgType, conference, nick, u'клиент глюк, инфы не хватает');
		else:
			sendMsg(msgType, conference, nick, u'глючит клиент');

registerCommand(showVersion, u'версия', 10, u'Показывает информацию о клиенте указанного пользователя', u'версия [ник]', (u'версия', u'версия Nick'));
