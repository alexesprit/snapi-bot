# protocol.py

# Copyright (C) 2003-2005 Alexey "Snake" Nezhdanov

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# $Id: protocol.py,v 1.60 2009/04/07 11:14:28 snakeru Exp $

"""
	Protocol module contains tools that is needed for processing of 
	xmpp-related data structures.
"""

import time

from simplexml import Node

NS_DATA							= "jabber:x:data"								#XEP-0004
NS_RPC							= "jabber:iq:rpc"								#XEP-0009
NS_LAST							= "jabber:iq:last"								#XEP-0012
NS_OFFLINE						= "http://jabber.org/protocol/offline"			#XEP-0013
NS_PRIVACY						= "jabber:iq:privacy"							#XEP-0016
NS_FEATURE						= "http://jabber.org/protocol/feature-neg"		#XEP-0020
NS_EVENT						= "jabber:x:event"								#XEP-0022 (obsolete)
NS_ENCRYPTED					= "jabber:x:encrypted"							#XEP-0027
NS_DISCO						= "http://jabber.org/protocol/disco"			#XEP-0030
NS_DISCO_INFO				 	= "http://jabber.org/protocol/disco#info"		#XEP-0030
NS_DISCO_ITEMS					= "http://jabber.org/protocol/disco#items"		#XEP-0030
NS_ADDRESS		  				= "http://jabber.org/protocol/address"			#XEP-0033
NS_STATS						= "http://jabber.org/protocol/stats"			#XEP-0039
NS_MUC							= "http://jabber.org/protocol/muc"				#XEP-0045
NS_MUC_ADMIN					= "http://jabber.org/protocol/muc#admin"		#XEP-0045
NS_MUC_USER						= "http://jabber.org/protocol/muc#user"			#XEP-0045
NS_IBB							= "http://jabber.org/protocol/ibb"				#XEP-0047
NS_PRIVATE						= "jabber:iq:private"							#XEP-0049
NS_COMMANDS						= "http://jabber.org/protocol/commands"			#XEP-0050
NS_VCARD						= "vcard-temp"									#XEP-0054
NS_SEARCH						= "jabber:iq:search"							#XEP-0055
NS_RSM							= "http://jabber.org/protocol/rsm"				#XEP-0059
NS_PUBSUB						= "http://jabber.org/protocol/pubsub"			#XEP-0060
NS_BYTESTREAM					= "http://jabber.org/protocol/bytestreams"		#XEP-0065
NS_OOB							= "jabber:x:oob"								#XEP-0065
NS_XHTML_IM						= "http://jabber.org/protocol/xhtml-im"			#XEP-0071
NS_EVIL							= "http://jabber.org/protocol/evil"				#XEP-0076
NS_REGISTER						= "jabber:iq:register"							#XEP-0077
NS_AUTH							= "jabber:iq:auth"								#XEP-0078
NS_AMP			  				= "http://jabber.org/protocol/amp"				#XEP-0079
NS_GEOLOC						= "http://jabber.org/protocol/geoloc"			#XEP-0080
NS_AVATAR						= "urn:xmpp:avatar"								#XEP-0084
NS_CHATSTATES					= "http://jabber.org/protocol/chatstates"		#XEP-0085
NS_TIME							= "jabber:iq:time"								#XEP-0090 (deprecated)
NS_DELAY						= "jabber:x:delay"								#XEP-0091 (deprecated)
NS_VERSION						= "jabber:iq:version"							#XEP-0092
NS_SI							= "http://jabber.org/protocol/si"				#XEP-0096
NS_GATEWAY						= "jabber:iq:gateway"							#XEP-0096
NS_MOOD							= "http://jabber.org/protocol/mood"				#XEP-0107
NS_ACTIVITY		 				= "http://jabber.org/protocol/activity"			#XEP-0108
NS_PHYSLOC						= "http://jabber.org/protocol/physloc"			#XEP-0112
NS_COMPONENT_ACCEPT				= "jabber:component:accept"						#XEP-0114
NS_CAPS							= "http://jabber.org/protocol/caps"				#XEP-0115
NS_TUNE							= "http://jabber.org/protocol/tune"				#XEP-0118
NS_WAITINGLIST					= "http://jabber.org/protocol/waitinglist"		#XEP-0130
NS_SHIM							= "http://jabber.org/protocol/shim"				#XEP-0131
NS_COMPRESS						= "http://jabber.org/protocol/compress"			#XEP-0138
NS_ROSTERX						= "http://jabber.org/protocol/rosterx"			#XEP-0144
NS_JINGLE						= "urn:xmpp:jingle:1"							#XEP-0167
NS_RECEIPTS						= "urn:xmpp:receipts"							#XEP-0184
NS_PING							= "urn:xmpp:ping"								#XEP-0199
NS_ENTITY_TIME					= "urn:xmpp:time"								#XEP-0202
NS_URN_DELAY					= "urn:xmpp:delay"								#XEP-0204
NS_ATTENTION					= "urn:xmpp:attention:0"						#XEP-0224

NS_BIND							= "urn:ietf:params:xml:ns:xmpp-bind"			#RFC 3920
NS_SASL							= "urn:ietf:params:xml:ns:xmpp-sasl"			#RFC 3920
NS_STANZAS						= "urn:ietf:params:xml:ns:xmpp-stanzas"			#RFC 3920
NS_STREAMS						= "http://etherx.jabber.org/streams"			#RFC 3920
NS_TLS							= "urn:ietf:params:xml:ns:xmpp-tls"				#RFC 3920
NS_XMPP_STREAMS					= "urn:ietf:params:xml:ns:xmpp-streams"			#RFC 3920
NS_CLIENT						= "jabber:client"								#RFC 3921
NS_ROSTER						= "jabber:iq:roster"							#RFC 3921
NS_SESSION						= "urn:ietf:params:xml:ns:xmpp-session"			#RFC 3921

NS_IQ							= "iq"											#Jabberd2
NS_MESSAGE						= "message"										#Jabberd2
NS_PRESENCE						= "presence"									#Jabberd2

TYPE_PRIVATE = "chat"
TYPE_PUBLIC = "groupchat"
TYPE_ERROR = "error"
TYPE_HEADLINE = "headline"
TYPE_NORMAL = "normal"
TYPE_RESULT = "result"
TYPE_GET = "get"
TYPE_SET = "set"

PRS_OFFLINE = "unavailable"
PRS_ONLINE = "online"
PRS_CHAT = "chat"
PRS_AWAY = "away"
PRS_DND = "dnd"
PRS_NA = "xa"

PRS_SUBSCRIBE = "subscribe"
PRS_SUBSCRIBED = "subscribed"
PRS_UNSUBSCRIBE = "unsubscribe"
PRS_UNSUBSCRIBED = "unsubscribed"

ROLE_NONE = "none"
ROLE_VISITOR = "visitor"
ROLE_PARTICIPANT = "participant"
ROLE_MODERATOR = "moderator"

AFF_OUTCAST = "outcast"
AFF_NONE = "none"
AFF_MEMBER = "member"
AFF_ADMIN = "admin"
AFF_OWNER = "owner"

ITEM_JID = "jid"
ITEM_NICK = "nick"

class NodeProcessed(Exception):
	""" Exception that should be raised by handler 
		when the handling should be stopped. 
	"""

class StreamError(Exception):
	""" Exception class for stream errors.
	"""

class UserJID:
	""" UserJID object.
	"""
	def __init__(self, jid):
		""" Constructor. JID must be specified as string.
		"""
		if isinstance(jid, UserJID):
			self.node = jid.getNode()
			self.domain = jid.getDomain()
			self.resource= jid.getResource()
		else:
			if jid.count("/"):
				barejid, self.resource = jid.split("/", 1)
			else:
				barejid = jid
				self.resource = None
			if barejid.count("@"):
				self.node, self.domain = barejid.split("@", 1)
			else:
				self.node = None
				self.domain = barejid

	def getNode(self):
		""" Return the node part of jid.
		"""
		return self.node

	def getDomain(self):
		""" Return the domain part of jid.
		"""
		return self.domain

	def getResource(self):
		""" Return the resource part of jid.
		"""
		return self.resource

	def getBareJID(self):
		""" Return the bare representation of jid. I.e. string value w/o resource.
		"""
		return self.__str__(False)

	def __str__(self, showResource=True):
		""" Serialise UserJID into string.
		"""
		if self.node:
			jid = "%s@%s" % (self.node, self.domain)
		else:
			jid = self.domain
		if showResource and self.resource:
			return "%s/%s" % (jid, self.resource)
		return jid

class Stanza(Node):
	""" A "stanza" object class. Contains methods that are common for presences, iqs and messages.
	"""
	def __init__(self, name=None, to=None, typ=None, frm=None, attrs=None, xmlns=NS_CLIENT, node=None):
		""" Constructor, name is the name of the stanza i.e. "message" or "presence" or "iq".
			to is the value of "to" attribure, "typ" - "type" attribute
			frn - from attribure, attrs - other attributes mapping, payload - same meaning as for simplexml payload definition
			xmlns - namespace of top stanza node
			node - parsed or unparsed stana to be taken as prototype.
		"""
		if not attrs:
			attrs = {}
		if to:
			attrs["to"] = to
		if frm:
			attrs["from"] = frm
		if typ:
			attrs["type"] = typ
		Node.__init__(self, name=name, attrs=attrs, node=node)
		if xmlns and not node:
			self.setXMLNS(xmlns)
		to = self.getAttr("to")
		if to:
			self.setTo(to)
		frm = self.getAttr("from")
		if frm:
			self.setFrom(frm)

	def setFrom(self, value):
		""" Set the value of the "from" attribute.
		"""
		self.setAttr("from", UserJID(value))

	def getFrom(self):
		""" Return value of the "from" attribute.
		"""
		return self.getAttr("from")

	def getTo(self):
		""" Return value of the "to" attribute.
		"""
		return self.getAttr("to")

	def setTo(self, value):
		""" Set the value of the "to" attribute.
		"""
		self.setAttr("to", UserJID(value))

	def getID(self):
		""" Return the value of the "id" attribute.
		"""
		return self.getAttr("id")

	def setID(self, value):
		""" Set the value of the "id" attribute.
		"""
		self.setAttr("id", value)

	def getType(self):
		""" Return the value of the "type" attribute.
		"""
		return self.getAttr("type")
	
	def setType(self, value):
		""" Set the value of the "type" attribute.
		"""
		self.setAttr("type", value)

	def getErrorCode(self):
		""" Return the error code. Obsolette.
		"""
		return self.getTagAttr("error", "code")
	
	def getProperties(self):
		""" Return the list of namespaces to which belongs the direct childs of element.
		"""
		props = []
		for child in self.getChildren():
			prop = child.getXMLNS()
			if prop not in props:
				props.append(prop)
		return props

class Message(Stanza):
	""" XMPP Message stanza - "push" mechanism.
	"""
	def __init__(self, to=None, typ=None, body=None, subject=None, attrs=None, frm=None, xmlns=NS_CLIENT, node=None):
		""" Create message object. You can specify recipient, text of message, type of message
			any additional attributes, sender of the message, any additional payload (f.e. jabber:x:delay element) and namespace in one go.
			Alternatively you can pass in the other XML object as the "node" parameted to replicate it as message.
		"""
		Stanza.__init__(self, NS_MESSAGE, to=to, typ=typ, attrs=attrs, frm=frm, xmlns=xmlns, node=node)
		if body:
			self.setBody(body)
		if subject:
			self.setSubject(subject)
	
	def getBody(self):
		""" Returns text of the message.
		"""
		return self.getTagData("body")

	def setBody(self, body):
		""" Sets the text of the message.
		"""
		self.setTagData("body", body)

	def getSubject(self):
		""" Returns subject of the message.
		"""
		return self.getTagData("subject")

	def setSubject(self, subject):
		""" Sets the subject of the message.
		"""
		self.setTagData("subject", subject)

	def isOffline(self):
		""" Return the True if message is offline.
		"""
		delay = self.getTag("x", xmlns=NS_DELAY)
		if delay:
			return delayNode.hasAttr("stamp")
		return False

class Presence(Stanza):
	""" XMPP Presence object.
	"""
	def __init__(self, to=None, typ=None, priority=None, show=None, status=None, attrs=None, frm=None, xmlns=NS_CLIENT, node=None):
		""" Create presence object. You can specify recipient, type of message, priority, show and status values
			any additional attributes, sender of the presence, any additional payload (f.e. jabber:x:delay element) and namespace in one go.
			Alternatively you can pass in the other XML object as the "node" parameted to replicate it as presence.
		"""
		Stanza.__init__(self, NS_PRESENCE, to=to, typ=typ, attrs=attrs, frm=frm, xmlns=xmlns, node=node)
		if priority:
			self.setPriority(priority)
		if show:
			self.setShow(show)
		if status:
			self.setStatus(status)
	
	def getPriority(self):
		""" Returns the priority of the message.
		"""
		return self.getTagData("priority")

	def setPriority(self, priority):
		""" Sets the priority of the presence.
		"""
		self.setTagData("priority", priority)

	def getShow(self):
		""" Returns the show value of the message.
		"""
		return self.getTagData("show")

	def setShow(self, show):
		""" Sets the show value of the message.
		"""
		self.setTagData("show", show)

	def getStatus(self):
		""" Returns the status string of the message.
		"""
		return self.getTagData("status")

	def setStatus(self, status):
		""" Sets the status string of the message.
		"""
		self.setTagData("status", status)

	def _getMUCItemAttr(self, tag, attr):
		for xtag in self.getTags("x", {}, NS_MUC_USER):
			for child in xtag.getTags(tag):
				return child.getAttr(attr)
	
	def getRole(self):
		"""Returns the presence role.
		"""
		return self._getMUCItemAttr("item", "role")
	
	def getAffiliation(self):
		"""Returns the presence affiliation.
		"""
		return self._getMUCItemAttr("item", "affiliation")
		
	def getNick(self):
		"""Returns the presence nick.
		"""
		return self._getMUCItemAttr("item", "nick")
	
	def getJID(self):
		"""Returns the presence jid.
		"""
		return self._getMUCItemAttr("item", "jid")
	
	def getStatusCode(self):
		"""Returns the status code of the presence.
		"""
		return self._getMUCItemAttr("status", "code")

class Iq(Stanza): 
	""" XMPP Iq object - get/set dialog mechanism.
	"""
	def __init__(self, typ=None, qxmlns=None, attrs=None, to=None, frm=None, xmlns=NS_CLIENT, node=None):
		""" Create Iq object. You can specify type, query namespace
			any additional attributes, recipient of the iq, sender of the iq, any additional payload (f.e. jabber:x:data node) and namespace in one go.
			Alternatively you can pass in the other XML object as the "node" parameted to replicate it as an iq
		"""
		Stanza.__init__(self, NS_IQ, to=to, typ=typ, attrs=attrs, frm=frm, xmlns=xmlns, node=node)
		if qxmlns:
			self.setQueryXMLNS(qxmlns)

	def getQueryXMLNS(self):
		""" Return the namespace of the "query" child element.
		"""
		tag = self.getTag("query")
		if tag:
			return tag.getXMLNS()

	def setQueryXMLNS(self, xmlns):
		""" Set the namespace of the "query" child element.
		"""
		self.setTag("query").setXMLNS(xmlns)

	def getQueryChildren(self):
		""" Return the "query" child element child nodes.
		"""
		tag = self.getTag("query")
		if tag:
			return tag.getChildren()

	def getQueryNode(self):
		return self.getTag("query")

	def setQueryPayload(self, payload):
		""" Set the "query" child element payload.
		"""
		self.setTag("query").setPayload(payload)

	def buildReply(self, typ):
		""" Builds and returns another Iq object of specified type.
			The to, from and query child node of new Iq are pre-set as reply to this Iq
		"""
		iq = Iq(typ, to=self.getFrom(), frm=self.getTo(), attrs={"id": self.getID()})
		if self.getTag("query"):
			iq.setQueryXMLNS(self.getQueryXMLNS())
		return iq
