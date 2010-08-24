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

def _showSomeList(stanza, mucID, type, conference, nick):
	if(mucID == stanza.getID()):
		if(stanza.getType() == 'result'):
			items = [u'%d) %s' % (i + 1, p.getAttrs()['jid']) for i, p in enumerate(stanza.getQueryChildren())];
			if(items):
				message = u'смотри, что я нашла:\n';
				if(type == PUBLIC):
					sendMsg(type, conference, nick, u'смотри в привате');
				sendMsg(PRIVATE, conference, nick, message + '\n'.join(items));
			else:
				sendMsg(type, conference, nick, u'список пуст');
		else:
			sendMsg(type, conference, nick, u'не получается :(');

def showSomeList(type, conference, nick, aff):
	iq = xmpp.Iq('get', xmpp.NS_MUC_ADMIN, payload = [xmpp.Node('item', {'affiliation': aff})]);
	iq.setTo(conference);
	mucID = getUniqueID(MUC_ID);
	iq.setID(mucID);
	gClient.SendAndCallForResponse(iq, _showSomeList, (mucID, type, conference, nick, ));

def showBanList(type, conference, nick, param):
	showSomeList(type, conference, nick, AFF_OUTCAST);

registerCommandHandler(showBanList, u'банлист', 20, u'Показывает список забаненных', u'банлист', (u'банлист', ), CHAT | NONPARAM);

def showMemberList(type, conference, nick, param):
	showSomeList(type, conference, nick, AFF_MEMBER);

registerCommandHandler(showMemberList, u'мемберлист', 20, u'Показывает список мемберов', u'мемберлист', (u'мемберлист', ), CHAT | NONPARAM);

def showAdminList(type, conference, nick, param):
	showSomeList(type, conference, nick, AFF_ADMIN);

registerCommandHandler(showAdminList, u'админлист', 20, u'Показывает список админов', u'админлист', (u'админлист', ), CHAT | NONPARAM);

def showOwnerList(type, conference, nick, param):
	showSomeList(type, conference, nick, AFF_OWNER);

registerCommandHandler(showOwnerList, u'овнерлист', 20, u'Показывает список овнеров', u'овнерлист', (u'овнерлист', ), CHAT | NONPARAM);
