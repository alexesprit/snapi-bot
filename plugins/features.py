# coding: utf-8

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

FEAT_ID = "features_id"

FEATURES = {
			xmpp.NS_DATA:			"XEP-0004: Data Forms",
			xmpp.NS_RPC:			"XEP-0009: Jabber-RPC",
			xmpp.NS_LAST:			"XEP-0012: Last Activity",
			xmpp.NS_OFFLINE:		"XEP-0013: Flexible Offline Message Retrieval",
			xmpp.NS_PRIVACY:		"XEP-0016: Privacy Lists",
			xmpp.NS_FEATURE: 		"XEP-0020: Feature Negotiation",
			xmpp.NS_EVENT: 			"XEP-0022: Message Events",
			xmpp.NS_ENCRYPTED:		"XEP-0027: Current OpenPGP Usage",
			xmpp.NS_DISCO: 			"XEP-0030: Service Discovery",
			xmpp.NS_ADDRESS:		"XEP-0033: Extended Stanza Addressing",
			xmpp.NS_MUC:			"XEP-0045: Multi-User Chat",
			xmpp.NS_IBB: 			"XEP-0047: In-Band Bytestreams",
			xmpp.NS_PRIVATE: 		"XEP-0049: Private XML Storage",
			xmpp.NS_COMMANDS: 		"XEP-0050: Ad-Hoc Commands",
			xmpp.NS_VCARD:			"XEP-0054: User VCard",
			xmpp.NS_RSM:			"XEP-0059: Result Set Management",
			xmpp.NS_PUBSUB:			"XEP-0060: Publish-Subscribe",
			xmpp.NS_BYTESTREAM:		"XEP-0065: SOCKS5 Bytestreams",
			xmpp.NS_OOB:			"XEP-0066: Out of Band Data",
			xmpp.NS_XHTML_IM:		"XEP-0071: XHTML-IM",
			xmpp.NS_EVIL:			"XEP-0071: Malicious Stanzas",
			xmpp.NS_AMP:			"XEP-0079: Advanced Message Processing",
			xmpp.NS_GEOLOC:			"XEP-0080: User Geolocation",
			xmpp.NS_AVATAR:			"XEP-0084: User Avatar",
			xmpp.NS_CHATSTATES:		"XEP-0085: Chat State Notifications",
			xmpp.NS_TIME:			"XEP-0090: XMPP Time",
			xmpp.NS_VERSION:		"XEP-0092: Software Version",
			xmpp.NS_SI:				"XEP-0096: SI File Transfer",
			xmpp.NS_MOOD:			"XEP-0107: User Mood",
			xmpp.NS_ACTIVITY:		"XEP-0108: User Activity",
			xmpp.NS_CAPS:			"XEP-0115: Entity Capabilities",
			xmpp.NS_ACTIVITY:		"XEP-0118: User Tune",
			xmpp.NS_SHIM:			"XEP-0131: Stanza Headers and Internet Metadata",
			xmpp.NS_COMPRESS: 		"XEP-0138: Stream Compression",
			xmpp.NS_ROSTERX:		"XEP-0144: Roster Item Exchange",
			xmpp.NS_WAITINGLIST:	"XEP-0130: Waiting Lists",
			xmpp.NS_RECEIPTS:		"XEP-0184: Message Receipts",
			xmpp.NS_PING:			"XEP-0199: XMPP Ping",
			xmpp.NS_ENTITY_TIME:	"XEP-0202: Entity Time",
			xmpp.NS_ATTENTION:		"XEP-0224: Attention",
			xmpp.NS_JINGLE:			"XEP-0234: Jingle File Transfer",
}

gFeatList = FEATURES.keys()

def showFeatures(msgType, conference, nick, param):
	if(param):
		if(conferenceInList(conference) and nickIsOnline(conference, param)):
			jid = conference + "/" + param
		else:
			jid = param
	else:
		jid = conference + "/" + nick
	iq = xmpp.Iq(xmpp.TYPE_GET)
	iq.setTo(jid)
	iq.addChild("query", {}, [], xmpp.NS_DISCO_INFO)
	iq.setID(getUniqueID(FEAT_ID))
	gClient.sendAndCallForResponse(iq, _showFeatures, (msgType, conference, nick, param, ))

def _showFeatures(stanza, msgType, conference, nick, param):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		featList = set()
		for p in stanza.getQueryChildren():
			attr = p.getAttrs()
			if("var" in attr):
				for feat in attr["var"].split():
					for y in FEATURES:
						if(feat.count(y)):
							featList.add(FEATURES[y])
		if(featList):
			featList = list(featList)
			featList.sort()
			answer = u"вот, что я узнала:\n%s" % ("\n".join(featList))
			if(xmpp.TYPE_PUBLIC == msgType):
				sendMsg(msgType, conference, nick, u"ушли")
			sendMsg(xmpp.TYPE_PRIVATE, conference, nick, answer)
		else:
			sendMsg(msgType, conference, nick, u"нет инфы")
	else:
		sendMsg(msgType, conference, nick, u"не могу :(")
		
registerCommand(showFeatures, u"фичи", 10, 
				u"Показывает, какие XEP-ы подерживает клиент указанного пользователя или сервер", 
				u"фичи [ник|сервер]", 
				(u"фичи", u"фичи Nick", u"фичи server.tld"))
