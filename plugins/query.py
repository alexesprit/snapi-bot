# coding: utf-8

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

BOT_FEATURES = (
	protocol.NS_DISCO_INFO,
	protocol.NS_DISCO_ITEMS,
	protocol.NS_MUC,
	protocol.NS_CAPS,
	protocol.NS_RECEIPTS,
	protocol.NS_MOOD,
	protocol.NS_ACTIVITY,
	protocol.NS_PING,
	protocol.NS_VERSION,
	protocol.NS_VCARD,
	protocol.NS_ENTITY_TIME
)

def processIqStanzas(stanza, jid, resource):
	if(protocol.TYPE_ERROR != stanza.getType()):
		if(stanza.getTags("query", {}, protocol.NS_VERSION)):
			iq = stanza.buildReply(protocol.TYPE_RESULT)
			query = iq.getTag("query")
			query.setTagData("name", gVersion[0])
			query.setTagData("version", gVersion[1])
			query.setTagData("os", gVersion[2])
		elif(stanza.getTags("query", {}, protocol.NS_LAST)):
			iq = stanza.buildReply(protocol.TYPE_RESULT)
			query = iq.getTag("query")
			query.setAttr("seconds", int(time.time() - gInfo["start"]))
		elif(stanza.getTags("time", {}, protocol.NS_ENTITY_TIME)):
			tZone = time.altzone if time.daylight else time.timezone
			sign = (tZone < 0) and "+" or "-"
			tzo = "%s%02d:%02d" % (sign, abs(tZone) / 3600, abs(tZone) / 60 % 60)
			utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
			iq = stanza.buildReply(protocol.TYPE_RESULT)
			tNode = iq.addChild("time", {}, [], protocol.NS_ENTITY_TIME)
			tNode.setTagData("tzo", tzo)
			tNode.setTagData("utc", utc)
		elif(stanza.getTags("ping", {}, protocol.NS_PING)):
			iq = stanza.buildReply(protocol.TYPE_RESULT)
		elif(stanza.getTags("query", {}, protocol.NS_DISCO_INFO)):
			iq = stanza.buildReply(protocol.TYPE_RESULT)
			query = iq.addChild("query", {}, [], protocol.NS_DISCO_ITEMS)
			query.addChild("identity", {"category": "client", "type": "phone", "name": "Jimm"})
			for feat in BOT_FEATURES:
				query.addChild("feature", {"var": feat})
		else:
			iq = stanza.buildReply(protocol.TYPE_ERROR)
			error = iq.addChild("error", {"type": "cancel"})
			error.addChild("feature-not-implemented", {}, [], protocol.NS_STANZAS)
		gClient.send(iq)

registerIqHandler(processIqStanzas)
