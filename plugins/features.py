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

XMPP_FEATURES = {
	protocol.NS_DATA:			"XEP-0004: Data Forms",
	protocol.NS_RPC:			"XEP-0009: Jabber-RPC",
	protocol.NS_LAST:			"XEP-0012: Last Activity",
	protocol.NS_OFFLINE:		"XEP-0013: Flexible Offline Message Retrieval",
	protocol.NS_PRIVACY:		"XEP-0016: Privacy Lists",
	protocol.NS_FEATURE: 		"XEP-0020: Feature Negotiation",
	protocol.NS_EVENT: 			"XEP-0022: Message Events",
	protocol.NS_ENCRYPTED:		"XEP-0027: Current OpenPGP Usage",
	protocol.NS_DISCO: 			"XEP-0030: Service Discovery",
	protocol.NS_ADDRESS:		"XEP-0033: Extended Stanza Addressing",
	protocol.NS_MUC:			"XEP-0045: Multi-User Chat",
	protocol.NS_IBB: 			"XEP-0047: In-Band Bytestreams",
	protocol.NS_PRIVATE: 		"XEP-0049: Private XML Storage",
	protocol.NS_COMMANDS: 		"XEP-0050: Ad-Hoc Commands",
	protocol.NS_VCARD:			"XEP-0054: User VCard",
	protocol.NS_SEARCH:			"XEP-0055: Jabber Search",
	protocol.NS_RSM:			"XEP-0059: Result Set Management",
	protocol.NS_PUBSUB:			"XEP-0060: Publish-Subscribe",
	protocol.NS_BYTESTREAM:		"XEP-0065: SOCKS5 Bytestreams",
	protocol.NS_OOB:			"XEP-0066: Out of Band Data",
	protocol.NS_XHTML_IM:		"XEP-0071: XHTML-IM",
	protocol.NS_EVIL:			"XEP-0076: Malicious Stanzas",
	protocol.NS_REGISTER:		"XEP-0077: In-Band Registration",
	protocol.NS_AMP:			"XEP-0079: Advanced Message Processing",
	protocol.NS_GEOLOC:			"XEP-0080: User Geolocation",
	protocol.NS_AVATAR:			"XEP-0084: User Avatar",
	protocol.NS_CHATSTATES:		"XEP-0085: Chat State Notifications",
	protocol.NS_TIME:			"XEP-0090: Legacy Entity Time",
	protocol.NS_DELAY:			"XEP-0091: Legacy Delayed Delivery",
	protocol.NS_VERSION:		"XEP-0092: Software Version",
	protocol.NS_SI:				"XEP-0096: SI File Transfer",
	protocol.NS_GATEWAY:		"XEP-0100: Gateway Interaction",
	protocol.NS_MOOD:			"XEP-0107: User Mood",
	protocol.NS_ACTIVITY:		"XEP-0108: User Activity",
	protocol.NS_CAPS:			"XEP-0115: Entity Capabilities",
	protocol.NS_TUNE:			"XEP-0118: User Tune",
	protocol.NS_WAITINGLIST:	"XEP-0130: Waiting Lists",
	protocol.NS_SHIM:			"XEP-0131: Stanza Headers and Internet Metadata",
	protocol.NS_COMPRESS: 		"XEP-0138: Stream Compression",
	protocol.NS_ROSTERX:		"XEP-0144: Roster Item Exchange",
	protocol.NS_JINGLE:			"XEP-0167: Jingle RTP Sessions",
	protocol.NS_RECEIPTS:		"XEP-0184: Message Receipts",
	protocol.NS_PING:			"XEP-0199: XMPP Ping",
	protocol.NS_ENTITY_TIME:	"XEP-0202: Entity Time",
	protocol.NS_URN_DELAY:		"XEP-0203: Delayed Delivery",
	protocol.NS_ATTENTION:		"XEP-0224: Attention"
}

def showFeatures(msgType, conference, nick, param):
	if param:
		if conferenceInList(conference) and nickIsOnline(conference, param):
			jid = conference + "/" + param
		else:
			jid = param
	else:
		jid = conference + "/" + nick
	iq = protocol.Iq(protocol.TYPE_GET)
	iq.setTo(jid)
	iq.addChild("query", {}, [], protocol.NS_DISCO_INFO)
	iq.setID(getUniqueID("feat_id"))
	gClient.sendAndCallForResponse(iq, _showFeatures, (msgType, conference, nick, param))

def _showFeatures(stanza, msgType, conference, nick, param):
	if protocol.TYPE_RESULT == stanza.getType():
		featureList = set()
		queryNode = stanza.getQueryNode()
		for tag in queryNode.getTags("feature"):
			feature = tag.getAttr("var")
			for knownFeature in XMPP_FEATURES:
				if feature.count(knownFeature):
					featureList.add(XMPP_FEATURES[knownFeature])
		if featureList:
			featureList = list(featureList)
			featureList.sort()
			answer = u"Вот, что я узнала:\n%s" % ("\n".join(featureList))
			if protocol.TYPE_PUBLIC == msgType:
				sendMsg(msgType, conference, nick, u"Ушли")
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, answer)
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"Не могу :(")
		
registerCommand(showFeatures, u"фичи", 10, 
				u"Показывает, какие XEP-ы подерживает клиент указанного пользователя или сервер", 
				u"[ник|жид|сервер]", 
				(None, u"Nick", u"server.tld", u"user@server.tld"))
