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
				jid = param;
		else:
			jid = conference + '/' + nick;
		iq = xmpp.Iq(xmpp.TYPE_GET, xmpp.NS_VERSION);
		iq.setTo(jid);
		iq.setID(getUniqueID(VER_ID));
		gClient.SendAndCallForResponse(iq, _showVersion, (msgType, conference, nick, param, ));

def _showVersion(stanza, msgType, conference, nick, param):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		name, ver, os = '', '', '';
		for child in stanza.getQueryChildren():
			if(child.getName() == 'name'):
				name = child.getData();
			elif(child.getName() == 'version'):
				ver = child.getData();
			elif(child.getName() == 'os'):
				os = child.getData();
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
		sendMsg(msgType, conference, nick, u'не получается :(');

registerCommand(showVersion, u'версия', 10, u'Показывает информацию о клиенте указанного пользователя', u'версия [ник]', (u'версия', u'версия Nick'));
