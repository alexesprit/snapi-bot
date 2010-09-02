# coding: utf-8;

# invite.py
# Initial Copyright (c) 2008 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def sendInvite(msgType, conference, nick, param):
	reason = '';
	if(not param.count('@')):
		userNick = param.split()[0];
		if(nickInConference(conference, userNick)):
			trueJid = getTrueJid(conference, userNick);
			reason = ' '.join(param.split()[1:]);
		else:
			return;
	else:
		trueJid = param;
	msg = xmpp.Message(to = conference)
	x = xmpp.Node('x')
	x.setNamespace('http://jabber.org/protocol/muc#user')
	inv = x.addChild('invite', {'to': trueJid})
	if reason:
		inv.setTagData('reason', reason)
	else:
		inv.setTagData('reason', u'Вас приглашает ' + nick)
	msg.addChild(node = x)
	gClient.send(msg);
	sendMsg(msgType, conference, nick, u'кинула инвайт');
			
registerCommand(sendInvite, u'призвать', 10, u'Приглашет заданного пользователя в конференцию', u'призвать <ник/жид> [причина]', (u'призвать guy', u'призвать guy@jabber.aq есть дело'), CHAT | PARAM);
