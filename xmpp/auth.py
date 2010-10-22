# auth.py

# Copyright (C) 2003-2005 Alexey "Snake" Nezhdanov

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2,  or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# $Id: auth.py, v 1.41 2008/09/13 21:45:21 normanr Exp $

"""
	Provides library with all SASL authentication mechanisms.
	Can be used both for client and transport authentication.
"""

import base64
import hashlib
import random
import re

import dispatcher

from protocol import Node, NodeProcessed, Stanza, UserJid
from protocol import NS_BIND, NS_SASL, NS_SESSION, NS_STREAMS
from protocol import TYPE_RESULT, TYPE_SET

from plugin import PlugIn

def HH(some):
	return hashlib.md5(some).hexdigest()
def H(some):
	return hashlib.md5(some).digest()
def C(some):
	return ":".join(some)

DBG_AUTH = "auth"
DBG_BIND = "bind"

AUTH_FAILURE = 0x0
AUTH_WAITING = 0x1
AUTH_SUCCESS = 0x2

BIND_FAILURE = 0x0
BIND_WAITING = 0x1
BIND_BINDING = 0x2
BIND_SUCCESS = 0x3

class SASL(PlugIn):
	""" Implements SASL authentication. """
	def __init__(self, username, password):
		PlugIn.__init__(self)
		self.username = username
		self.password = password
		self.debugFlag = DBG_AUTH
		self.state = None

	def auth(self):
		""" Start authentication. Result can be obtained via "SASL.state" attribute and will be
			either "success" or "failure". Note that successfull auth will take at least
			two Dispatcher.process() calls.
		"""
		try:
			self.FeaturesHandler(self._owner.Dispatcher, self._owner.Dispatcher.Stream.features)
		except NodeProcessed:
			pass

	def plugout(self):
		""" Remove SASL handlers from owner"s dispatcher. Used internally. """
		self._owner.unregisterHandler("challenge", self.SASLHandler, xmlns=NS_SASL)
		self._owner.unregisterHandler("failure", self.SASLHandler, xmlns=NS_SASL)
		self._owner.unregisterHandler("success", self.SASLHandler, xmlns=NS_SASL)

	def FeaturesHandler(self, conn, feats):
		""" Used to determine if server supports SASL auth. Used internally. """
		if not feats.getTag("mechanisms", namespace=NS_SASL):
			self.state = AUTH_FAILURE
			self.printf("SASL not supported by server", "error")
			return
		mecs = []
		for mec in feats.getTag("mechanisms", namespace=NS_SASL).getTags("mechanism"):
			mecs.append(mec.getData())
		self._owner.registerHandler("challenge", self.SASLHandler, xmlns=NS_SASL)
		self._owner.registerHandler("failure", self.SASLHandler, xmlns=NS_SASL)
		self._owner.registerHandler("success", self.SASLHandler, xmlns=NS_SASL)
		if "ANONYMOUS" in mecs and self.username is None:
			node = Node("auth", attrs={"xmlns": NS_SASL, "mechanism": "ANONYMOUS"})
		elif "DIGEST-MD5" in mecs:
			node = Node("auth", attrs={"xmlns": NS_SASL, "mechanism": "DIGEST-MD5"})
		elif "PLAIN" in mecs:
			saslData = "%s@%s\x00%s\x00%s" % (self.username, self._owner.Server, self.username, self.password)
			node = Node("auth", attrs={"xmlns": NS_SASL, "mechanism": "PLAIN"}, \
						payload=[base64.encodestring(saslData).replace("\r", "").replace("\n", "")])
		else:
			self.state = AUTH_FAILURE
			self.printf("I can only use DIGEST-MD5 and PLAIN mecanisms.", "error")
			return
		self.state = AUTH_WAITING
		self._owner.send(node.__str__())

	def SASLHandler(self, conn, challenge):
		""" Perform next SASL auth step. Used internally. """
		if challenge.getNamespace() != NS_SASL:
			return
		if challenge.getName() == "failure":
			self.state = AUTH_FAILURE
			children = challenge.getChildren()
			if(children):
				reason = children[0]
			else:
				reason = challenge
			self.printf("Failed SASL authentification: %s" % (reason), "error")
			raise NodeProcessed
		elif challenge.getName() == "success":
			self.state = AUTH_SUCCESS
			self.printf("Successfully authenticated with remote server", "ok")
			handlers = self._owner.Dispatcher.dumpHandlers()
			self._owner.Dispatcher.PlugOut()
			dispatcher.Dispatcher().PlugIn(self._owner)
			self._owner.Dispatcher.restoreHandlers(handlers)
			self._owner.User = self.username
			raise NodeProcessed

		incoming_data = challenge.getData()
		chal = {}
		data = base64.decodestring(incoming_data)
		self.printf("Got challenge: %s" % (data), "ok")
		for pair in re.findall(r'(\w+\s*=\s*(?:(?:"[^"]+")|(?:[^,]+)))', data):
			key, value = [x.strip() for x in pair.split("=",  1)]
			if value[:1] == "\"" and value[-1:] == "\"":
				value = value[1:-1]
			chal[key] = value
		if chal.has_key("qop") and "auth" in [x.strip() for x in chal["qop"].split(", ")]:
			resp={}
			resp["username"] = self.username
			resp["realm"] = self._owner.Server
			resp["nonce"] = chal["nonce"]
			cnonce = ""
			for i in range(7):
				cnonce += hex(int(random.random()*65536*4096))[2:]
			resp["cnonce"] = cnonce
			resp["nc"] = ("00000001")
			resp["qop"] = "auth"
			resp["digest-uri"] = "xmpp/" + self._owner.Server
			A1 = C([H(C([resp["username"], resp["realm"], self.password])), resp["nonce"], resp["cnonce"]])
			A2 = C(["AUTHENTICATE", resp["digest-uri"]])
			response = HH(C([HH(A1), resp["nonce"], resp["nc"], resp["cnonce"], resp["qop"], HH(A2)]))
			resp["response"] = response
			resp["charset"] = "utf-8"
			saslData = ""
			for key in ("charset", "username", "realm", "nonce", "nc", "cnonce", "digest-uri", "response", "qop"):
				if key in ("nc", "qop", "response", "charset"):
					saslData += "%s=%s, " % (key, resp[key])
				else:
					saslData += "%s=\"%s\", " % (key, resp[key])
			saslData = base64.encodestring(saslData[:-1]).replace("\r", "").replace("\n", "")
			node = Node("response", attrs={"xmlns": NS_SASL}, payload = [saslData])
			self._owner.send(node.__str__())
		elif chal.has_key("rspauth"):
			self._owner.send(Node("response", attrs={"xmlns": NS_SASL}).__str__())
		else: 
			self.state = AUTH_FAILURE
			self.printf("Failed SASL authentification: unknown challenge", "error")
		raise NodeProcessed

class Bind(PlugIn):
	""" Bind some UserJid to the current connection to allow router know of our location."""
	def __init__(self):
		PlugIn.__init__(self)
		self.debugFlag = DBG_BIND
		self.bound = BIND_WAITING

	def plugin(self, owner):
		""" Start resource binding,  if allowed at this time. Used internally. """
		self._owner.registerHandler("features", self.featuresHandler, xmlns=NS_STREAMS)

	def plugout(self):
		""" Remove Bind handler from owner's dispatcher. Used internally. """
		self._owner.unregisterHandler("features", self.featuresHandler, xmlns=NS_STREAMS)

	def featuresHandler(self, conn, feats):
		""" Determine if server supports resource binding and set some internal attributes accordingly. """
		if not feats.getTag("bind", namespace=NS_BIND):
			self.bound = BIND_FAILURE
			self.printf("Server does not requested binding.", "error")
			return
		self.bound = BIND_BINDING

	def bindResource(self, resource=None):
		""" Perform binding. Use provided resource name or random (if not provided). """
		while self.bound == BIND_WAITING and self._owner.process(1):
			pass
		if resource:
			resource = [Node("resource", payload=[resource])]
		else:
			resource = []
		stanza = self._owner.sendAndWaitForResponse(Stanza("iq", typ=TYPE_SET, payload=[Node("bind", attrs={"xmlns": NS_BIND}, payload=resource)]))
		stanzaType = stanza.getType()
		if stanzaType == TYPE_RESULT:
			resource = stanza.getTag("bind").getTagData("jid")
			self.printf("Successfully bound %s" % (resource), "ok")
			jid = UserJid(stanza.getTag("bind").getTagData("jid"))
			self._owner.User = jid.getNode()
			self._owner.Resource = jid.getResource()
			stanza = self._owner.sendAndWaitForResponse(Stanza("iq", typ=TYPE_SET, payload=[Node("session", attrs={"xmlns": NS_SESSION})]))
			stanzaType = stanza.getType()
			if stanzaType == TYPE_RESULT:
				self.printf("Successfully opened session", "ok")
				return BIND_SUCCESS
			else:
				self.printf("Session open failed", "error")
				return BIND_FAILURE
		else:
			if stanza:
				self.printf("Binding failed: %s" % (stanza.getTag("error")), "error")
			else:
				self.printf("Binding failed: timeout expired.", "error")
			return BIND_FAILURE
