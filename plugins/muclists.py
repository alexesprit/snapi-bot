# coding: utf-8;

# muclists.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

MUC_ID = 'muc_id';

def _showSomeList(stanza, msgType, conference, nick):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		items = [u'%d) %s' % (i + 1, p.getAttrs()['jid']) for i, p in enumerate(stanza.getQueryChildren())];
		if(items):
			message = u'смотри, что я нашла:\n';
			if(msgType == xmpp.TYPE_PUBLIC):
				sendMsg(msgType, conference, nick, u'смотри в привате');
			sendMsg(xmpp.TYPE_PRIVATE, conference, nick, message + '\n'.join(items));
		else:
			sendMsg(msgType, conference, nick, u'список пуст');
	else:
		sendMsg(msgType, conference, nick, u'не получается :(');

def showSomeList(msgType, conference, nick, aff):
	iq = xmpp.Iq(xmpp.TYPE_GET, xmpp.NS_MUC_ADMIN, payload = [xmpp.Node('item', {'affiliation': aff})]);
	iq.setTo(conference);
	iq.setID(getUniqueID(MUC_ID));
	gClient.SendAndCallForResponse(iq, _showSomeList, (msgType, conference, nick, ));

def showBanList(msgType, conference, nick, param):
	showSomeList(msgType, conference, nick, xmpp.AFF_OUTCAST);

registerCommand(showBanList, u'банлист', 20, u'Показывает список забаненных', None, (u'банлист', ), CHAT | NONPARAM);

def showMemberList(msgType, conference, nick, param):
	showSomeList(msgType, conference, nick, xmpp.AFF_MEMBER);

registerCommand(showMemberList, u'мемберлист', 20, u'Показывает список мемберов', None, (u'мемберлист', ), CHAT | NONPARAM);

def showAdminList(msgType, conference, nick, param):
	showSomeList(msgType, conference, nick, xmpp.AFF_ADMIN);

registerCommand(showAdminList, u'админлист', 20, u'Показывает список админов', None, (u'админлист', ), CHAT | NONPARAM);

def showOwnerList(msgType, conference, nick, param):
	showSomeList(msgType, conference, nick, xmpp.AFF_OWNER);

registerCommand(showOwnerList, u'овнерлист', 20, u'Показывает список овнеров', None, (u'овнерлист', ), CHAT | NONPARAM);
