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

def showVersion(type, conference, nick, param):
	if(param == getBotNick(conference)):
		sendMsg(type, conference, nick, u'я юзаю %s %s в %s' % (gVersion[0], gVersion[1], gVersion[2]));
	else:
		if(param):
			if(chatInList(conference) and nickOnlineInChat(conference, param)):
				jid = conference + '/' + param;
			else:
				return;
		else:
			jid = conference + '/' + nick;
		iq = xmpp.Iq('get', xmpp.NS_VERSION);
		iq.setTo(jid);
		verID = getUniqueID(VER_ID);
		iq.setID(verID);
		gClient.SendAndCallForResponse(iq, _showVersion, (verID, type, conference, nick, param, ));

def _showVersion(stanza, verID, type, conference, nick, param):
	if(verID == stanza.getID()):
		if(stanza.getType() == 'result'):
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
					sendMsg(type, conference, nick, u'ты юзаешь %s' % (version));
				else:
					sendMsg(type, conference, nick, u'%s юзает %s' % (param, version));
			else:
				sendMsg(type, conference, nick, u'глючит клиент');			

registerCommandHandler(showVersion, u'версия', 10, u'Показывает информацию о клиенте указанного пользователя', u'версия [ник]', (u'версия', u'версия Nick'));
