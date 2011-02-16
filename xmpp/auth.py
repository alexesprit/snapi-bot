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
import plugin
import protocol

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

class SASL(plugin.PlugIn):
	""" Implements SASL authentication.
	"""
	def __init__(self, username, password):
		plugin.PlugIn.__init__(self)

		self.debugFlag = DBG_AUTH
		self.username = username
		self.password = password
		self.state = None

	def plugin(self):
		self._owner.registerHandler("challenge", self._parseAuthStanza, xmlns=protocol.NS_SASL)
		self._owner.registerHandler("failure", self._parseAuthStanza, xmlns=protocol.NS_SASL)
		self._owner.registerHandler("success", self._parseAuthStanza, xmlns=protocol.NS_SASL)

	def plugout(self):
		""" Remove SASL handlers from owner's dispatcher.
			Used internally.
		"""
		self._owner.unregisterHandler("challenge", self._parseAuthStanza, xmlns=protocol.NS_SASL)
		self._owner.unregisterHandler("failure", self._parseAuthStanza, xmlns=protocol.NS_SASL)
		self._owner.unregisterHandler("success", self._parseAuthStanza, xmlns=protocol.NS_SASL)

	def auth(self):
		""" Start authentication. Result can be obtained via "SASL.state" attribute and will be
			either "success" or "failure". Note that successfull auth will take at least
			two Dispatcher.process() calls.
		"""
		features = self._owner.Dispatcher.stream.features
		if not features.getTag("mechanisms", namespace=protocol.NS_SASL):
			self.state = AUTH_FAILURE
			self.printf("SASL not supported by server", "error")
			return
		mecs = []
		for mec in features.getTag("mechanisms", namespace=protocol.NS_SASL).getTags("mechanism"):
			mecs.append(mec.getData())
		if "ANONYMOUS" in mecs and self.username is None:
			node = protocol.Node("auth", attrs={"xmlns": protocol.NS_SASL, "mechanism": "ANONYMOUS"})
		elif "DIGEST-MD5" in mecs:
			node = protocol.Node("auth", attrs={"xmlns": protocol.NS_SASL, "mechanism": "DIGEST-MD5"})
		elif "PLAIN" in mecs:
			saslData = "%s@%s\x00%s\x00%s" % (self.username, self._owner.server, self.username, self.password)
			node = protocol.Node("auth", attrs={"xmlns": protocol.NS_SASL, "mechanism": "PLAIN"}, \
						payload=[base64.encodestring(saslData).replace("\r", "").replace("\n", "")])
		else:
			self.state = AUTH_FAILURE
			self.printf("I can only use DIGEST-MD5 and PLAIN mecanisms.", "error")
			return
		self.state = AUTH_WAITING
		self._owner.send(node.__str__())

	def _parseAuthStanza(self, stanza):
		""" Perform next SASL auth step. Used internally.
		"""
		if stanza.getNamespace() != protocol.NS_SASL:
			return
		if stanza.getName() == "failure":
			self.state = AUTH_FAILURE
			children = stanza.getChildren()
			if children:
				reason = children[0]
			else:
				reason = stanza
			self.printf("Failed SASL authentification: %s" % (reason), "error")
			raise protocol.NodeProcessed
		elif stanza.getName() == "success":
			self.state = AUTH_SUCCESS
			self.printf("Successfully authenticated with remote server", "ok")
			handlers = self._owner.Dispatcher.dumpHandlers()
			self._owner.Dispatcher.plugOut()
			dispatcher.Dispatcher().plugIn(self._owner)
			self._owner.Dispatcher.restoreHandlers(handlers)
			self._owner._user = self.username
			raise protocol.NodeProcessed

		incoming_data = stanza.getData()
		chal = {}
		data = base64.decodestring(incoming_data)
		self.printf("Got challenge: %s" % (data), "ok")
		for pair in re.findall(r'(\w+\s*=\s*(?:(?:"[^"]+")|(?:[^,]+)))', data):
			key, value = [x.strip() for x in pair.split("=",  1)]
			if value[:1] == "\"" and value[-1:] == "\"":
				value = value[1:-1]
			chal[key] = value
		if "qop" in chal and "auth" in [x.strip() for x in chal["qop"].split(", ")]:
			resp={}
			resp["username"] = self.username
			resp["realm"] = self._owner.server
			resp["nonce"] = chal["nonce"]
			cnonce = ""
			for i in range(7):
				cnonce += hex(int(random.random()*65536*4096))[2:]
			resp["cnonce"] = cnonce
			resp["nc"] = ("00000001")
			resp["qop"] = "auth"
			resp["digest-uri"] = "xmpp/" + self._owner.server
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
			node = protocol.Node("response", attrs={"xmlns": protocol.NS_SASL}, payload=[saslData])
			self._owner.send(node.__str__())
		elif "rspauth" in chal:
			self._owner.send(protocol.Node("response", attrs={"xmlns": protocol.NS_SASL}).__str__())
		else: 
			self.state = AUTH_FAILURE
			self.printf("Failed SASL authentification: unknown challenge", "error")
		raise protocol.NodeProcessed

class Bind(plugin.PlugIn):
	""" Bind some jid to the current connection to allow router know of our location.
	"""
	def __init__(self):
		plugin.PlugIn.__init__(self)
		self.debugFlag = DBG_BIND
		self.bound = BIND_WAITING
	
	def plugin(self):
		self._owner.registerHandler("features", self._parseFeatures, xmlns=protocol.NS_STREAMS)

	def plugout(self):
		""" Remove Bind handler from owner's dispatcher. Used internally.
		"""
		self._owner.unregisterHandler("features", self._parseFeatures, xmlns=protocol.NS_STREAMS)

	def _parseFeatures(self, features):
		""" Determine if server supports resource binding and set some internal attributes accordingly.
		"""
		if not features.getTag("bind", namespace=protocol.NS_BIND):
			self.bound = BIND_FAILURE
			self.printf("Server does not requested binding.", "error")
			return
		self.bound = BIND_BINDING

	def bind(self, resource=None):
		""" Perform binding. Use provided resource name or random (if not provided).
		"""
		while self.bound == BIND_WAITING and self._owner.process(1):
			pass
		if resource:
			resource = [protocol.Node("resource", payload=[resource])]
		else:
			resource = []
		bNode = protocol.Node("bind", attrs={"xmlns": protocol.NS_BIND}, payload=resource)
		iq = protocol.Iq(typ=protocol.TYPE_SET, payload=[bNode])
		stanza = self._owner.sendAndWaitForResponse(iq)
		if protocol.TYPE_RESULT == stanza.getType():
			resource = stanza.getTag("bind").getTagData("jid")
			self.printf("Successfully bound %s" % (resource), "ok")

			jid = protocol.UserJID(stanza.getTag("bind").getTagData("jid"))
			self._owner.username = jid.getNode()
			self._owner.resource = jid.getResource()

			sNode = protocol.Node("session", attrs={"xmlns": protocol.NS_SESSION})
			iq = protocol.Iq(typ=protocol.TYPE_SET, payload=[sNode])
			stanza = self._owner.sendAndWaitForResponse(iq)
			if protocol.TYPE_RESULT == stanza.getType():
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
