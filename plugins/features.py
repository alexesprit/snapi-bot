# coding: utf-8;

# features.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

FEAT_ID = 'features_id';

FEATURES = {
xmpp.NS_DATA:				'XEP-0004: Data Forms',
xmpp.NS_RPC:				'XEP-0009: Jabber-RPC',
xmpp.NS_BROWSE:				'XEP-0011: Jabber Browsing',
xmpp.NS_LAST:				'XEP-0012: Last Activity',
xmpp.NS_OFFLINE:			'XEP-0013: Flexible Offline Message Retrieval',
xmpp.NS_FEATURE: 			'XEP-0020: Feature Negotiation',
xmpp.NS_EVENT:				'XEP-0022: Message Events',
xmpp.NS_ENCRYPTED:			'XEP-0027: Current OpenPGP Usage',
xmpp.NS_DISCO: 				'XEP-0030: Service Discovery',
xmpp.NS_ADDRESS:			'XEP-0033: Extended Stanza Addressing',
xmpp.NS_GROUPCHAT:			'XEP-0045: Multi-User Chat',
xmpp.NS_MUC:				'XEP-0045: Multi-User Chat',
xmpp.NS_IBB: 				'XEP-0047: In-Band Bytestreams',
xmpp.NS_PRIVATE:			'XEP-0049: Private XML Storage',
xmpp.NS_COMMANDS: 			'XEP-0050: Ad-Hoc Commands',
xmpp.NS_SEARCH:				'XEP-0055: Jabber Search',
xmpp.NS_VCARD:				'XEP-0054: User VCard',
xmpp.NS_PUBSUB:				'XEP-0060: Publish-Subscribe',
xmpp.NS_BYTESTREAM:			'XEP-0065: SOCKS5 Bytestreams',
xmpp.NS_XHTML_IM:			'XEP-0071: XHTML-IM',
xmpp.NS_SOAP:				'XEP-0072: SOAP Over XMPP',
xmpp.NS_REGISTER:			'XEP-0077: In-Band Registration',
xmpp.NS_AUTH:				'XEP-0078: Non-SASL Authentication',
xmpp.NS_AMP:				'XEP-0079: Advanced Message Processing',
xmpp.NS_GEOLOC:				'XEP-0080: User Geolocation',
xmpp.NS_PHYSLOC:			'XEP-0080: User Physlocation',
xmpp.NS_CHATSTATES: 		'XEP-0085: Chat State Notifications',
xmpp.NS_TIME:				'XEP-0090: XMPP Time',
xmpp.NS_VERSION:			'XEP-0092: Software Version',
xmpp.NS_ROSTERX:			'XEP-0093: Roster Item Exchange',
xmpp.NS_GATEWAY:			'XEP-0100: Gateway Interaction',
xmpp.NS_MOOD:				'XEP-0107: User Mood',
xmpp.NS_ACTIVITY:			'XEP-0108: User Activity',
xmpp.NS_COMPONENT_ACCEPT: 	'XEP-0114: Existing Component Protocol',
xmpp.NS_CAPS: 				'XEP-0115: Entity Capabilities',
xmpp.NS_DATA_VALIDATE:		'XEP-0122: Data Forms Validation',
xmpp.NS_HTTP_BIND:			'XEP-0124: Bidirectional-streams Over Synchronous HTTP',
xmpp.NS_SI_PUB:				'XEP-0137: Publishing SI Requests',
xmpp.NS_COMPRESS: 			'XEP-0138: Stream Compression',
xmpp.NS_ROSTERX:			'XEP-0144: Roster Item Exchange',
xmpp.NS_WAITINGLIST:		'XEP-0130: Waiting Lists',
xmpp.NS_DATA_LAYOUT:		'XEP-0141: Data Forms Layout',
xmpp.NS_RECEIPTS:			'XEP-0184: Message Receipts',
xmpp.NS_PING:				'XEP-0199: XMPP Ping',
xmpp.NS_ENTITY_TIME:		'XEP-0202: Entity Time',
xmpp.NS_DELAY:				'XEP-0203: Delayed Delivery',
xmpp.NS_ATTENTION:			'XEP-0224: Attention',
xmpp.NS_JINGLE:				'XEP-0234: Jingle File Transfer',
xmpp.NS_CLIENT: 			'RFC 3921: XMPP IM',
xmpp.NS_DIALBACK:			'RFC 3921: XMPP IM',
xmpp.NS_PRIVACY:			'RFC 3921: XMPP IM',
xmpp.NS_ROSTER:				'RFC 3921: XMPP IM',
};

gFeatList = FEATURES.keys();

def showFeatures(msgType, conference, nick, param):
	if(param):
		if(conferenceInList(conference) and nickIsOnline(conference, param)):
			jid = conference + '/' + param;
		else:
			sendMsg(msgType, conference, nick, u'а это кто?');
			return;
	else:
		jid = conference + '/' + nick;
	iq = xmpp.Iq(xmpp.TYPE_GET);
	iq.setTo(jid);
	iq.addChild('query', {}, [], 'http://jabber.org/protocol/disco#info');
	iq.setID(getUniqueID(FEAT_ID));
	gClient.SendAndCallForResponse(iq, _showFeatures, (msgType, conference, nick, param, ));

def _showFeatures(stanza, msgType, conference, nick, param):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		featList = set();
		for p in stanza.getQueryChildren():
			attr = p.getAttrs();
			if('var' in attr):
				for feat in attr['var'].split():
					for y in FEATURES:
						if(feat.count(y)):
							featList.add(FEATURES[y]);
		if(featList):
			featList = list(featList);
			featList.sort();
			if(param):
				answer = u'клиент %s поддерживает следующие стандарты:\n%s' % (param, '\n'.join(featList));
			else:
				answer = u'твой клиент поддерживает следующие стандарты:\n%s' % ('\n'.join(featList));
			if(xmpp.TYPE_PUBLIC == msgType):
				sendMsg(msgType, conference, nick, u'ушли');
			sendMsg(xmpp.TYPE_PRIVATE, conference, nick, answer);
		else:
			sendMsg(msgType, conference, nick, u'нет инфы');
	else:
		sendMsg(msgType, conference, nick, u'не могу :(');
		
registerCommand(showFeatures, u'фичи', 10, u'Показывает, какие XEP-ы подерживает клиент указанного пользователя', u'фичи [ник]', (u'фичи', u'фичи Nick'));
