# coding: utf-8;

# query.py
# Initial Copyright (с) ???
# Modification Copyright (с) -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

BOT_FEATURES = (xmpp.NS_DISCO_INFO,
			xmpp.NS_DISCO_ITEMS,
			xmpp.NS_MUC,
			xmpp.NS_MOOD,
			xmpp.NS_CAPS,
			xmpp.NS_RECEIPTS,
			xmpp.NS_ACTIVITY,
			xmpp.NS_PING,
			xmpp.NS_VERSION,
			xmpp.NS_PRIVACY,
			xmpp.NS_ROSTER,
			xmpp.NS_VCARD,
			xmpp.NS_ENTITY_TIME
			);

def processIqStanzas(stanza, jid, resource):
	if(not stanza.getType() == 'error'):
		if(stanza.getTags('query', {}, xmpp.NS_VERSION)):
			iq = stanza.buildReply('result');
			query = stanza.getTag('query');
			query.setTagData('name', gVersion[0]);
			query.setTagData('version', gVersion[1]);
			query.setTagData('os', gVersion[2]);
		elif(stanza.getTags('time', {}, xmpp.NS_ENTITY_TIME)):
			tzo = '%0.2d:00' % (time.daylight and time.altzone / -3600 or time.timezone / -3600);
			utc = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime());
			iq = stanza.buildReply('result');
			iq.addChild('time', {}, [], xmpp.NS_ENTITY_TIME);
			iq.setTagData('tzo', tzo);
			iq.setTagData('utc', utc);
		elif(stanza.getTags('ping', {}, xmpp.NS_PING)):
			iq = stanza.buildReply('result');
		elif(stanza.getTags('query', {}, xmpp.NS_DISCO_INFO)):
			iq = stanza.buildReply('result');
			query = iq.addChild('query', {}, [], xmpp.NS_DISCO_ITEMS);
			query.addChild('identity', {'category': 'client', 'type': 'phone', 'name': 'Jimm'});
			for feat in BOT_FEATURES:
				query.addChild('feature', {'var': feat});
		else:
			iq = stanza.buildReply('error');
			iq.addChild(node = stanza.getTag('query'));
			error = iq.addChild('error', {'type': 'cancel'});
			error.addChild('feature-not-implemented', {}, [], 'urn:ietf:params:xml:ns:xmpp-stanzas');
		gClient.send(iq);

registerIqHandler(processIqStanzas);
