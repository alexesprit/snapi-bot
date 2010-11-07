# dispatcher.py

# Copyright (C) 2003-2005 Alexey "Snake" Nezhdanov

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# $Id: dispatcher.py, v 1.42 2007/05/18 23:18:36 normanr Exp $

"""
	Main xmpppy mechanism. Provides library with methods to assign different handlers
	to different XMPP stanzas.
	Contains one tunable attribute: DEFAULT_TIMEOUT (25 seconds by default). It defines time that 
	Dispatcher.sendAndWaitForResponse method will wait for reply stanza before giving up.
"""

import time
import sys

import plugin
import protocol
import simplexml

DEFAULT_TIMEOUT = 25
gID = 0

DBG_DISPATCHER = "dispatcher"

class Dispatcher(plugin.PlugIn):
	""" Ancestor of PlugIn class. Handles XMPP stream, i.e. aware of stream headers.
		Can be plugged out/in to restart these headers (used for SASL f.e.).
	"""
	def __init__(self):
		plugin.PlugIn.__init__(self)
		self.debugFlag = DBG_DISPATCHER
		self.handlers = {}
		self._expected = {}
		self._exportedMethods = [
			self.process,
			self.registerHandler,
			self.unregisterHandler,
			self.sendAndWaitForResponse,
			self.waitForResponse,
			self.send,
			self.disconnect,
			self.sendAndCallForResponse
		]

	def dumpHandlers(self):
		""" Return set of user-registered callbacks in it's internal format.
			Used within the library to carry user handlers set over Dispatcher replugins. 
		"""
		return self.handlers

	def restoreHandlers(self, handlers):
		""" Restores user-registered callbacks structure from dump previously obtained via dumpHandlers.
			Used within the library to carry user handlers set over Dispatcher replugins. 
		"""
		self.handlers = handlers

	def _init(self):
		""" Registers default namespaces/protocols/handlers. Used internally.
		"""
		self.registerNamespace(protocol.NS_STREAMS)
		self.registerNamespace(self._owner.defaultNamespace)
		self.registerStanza("iq", protocol.Iq)
		self.registerStanza("presence", protocol.Presence)
		self.registerStanza("message", protocol.Message)
		self.registerHandler("error", self.streamErrorHandler, xmlns=protocol.NS_STREAMS)

	def plugin(self, owner):
		""" Plug the Dispatcher instance into Client class instance and send 
			initial stream header. Used internally.
		"""
		self._init()
		for method in self._oldMethods:
			if method.__name__ == "send":
				self._owner_send = method
				break
		self.initStream()

	def plugout(self):
		""" Prepares instance to be destructed.
		"""
		self.Stream.dispatch = None
		self.Stream.features = None
		self.Stream.destroy()

	def initStream(self):
		""" Send an initial stream header.
		"""
		self.Stream = simplexml.NodeBuilder()
		self.Stream._dispatch_depth = 2
		self.Stream.dispatch = self.dispatch
		self.Stream.stream_header_received = self._checkStreamStart
		self.Stream.features = None
		metastream = protocol.Node("stream:stream")
		metastream.setNamespace(self._owner.Namespace)
		metastream.setAttr("version", "1.0")
		metastream.setAttr("xmlns:stream", protocol.NS_STREAMS)
		metastream.setAttr("to", self._owner.Server)
		self._owner.send("<?xml version=\"1.0\"?>%s>" % str(metastream)[:-2])

	def _checkStreamStart(self, ns, tag, attrs):
		if ns != protocol.NS_STREAMS or tag != "stream":
			raise ValueError("Incorrect stream start: (%s, %s). Terminating." % (tag, ns))

	def process(self, timeout=0):
		""" Check incoming stream for data waiting. If "timeout" is positive - block for as max. this time.
			Returns:
				1) length of processed data if some data were processed
				2) "0" string if no data were processed but link is alive
				3) 0 (zero) if underlying connection is closed.
			Take note that in case of disconnection detect during process() call
			disconnect handlers are called automatically.
		"""
		if self._owner.Connection.pending_data(timeout):
			try:
				data = self._owner.Connection.receive()
			except IOError:
				return
			self.Stream.Parse(data)
			if data:
				return len(data)
		# It means that nothing is received but link is alive.
		return "0"
		
	def registerNamespace(self, xmlns, order="info"):
		""" Creates internal structures for newly registered namespace.
			You can register handlers for this namespace afterwards. By default one namespace
			already registered. 
		"""
		self.printf("Registering namespace %s" % (xmlns), order)
		self.handlers[xmlns] = {}
		self.registerStanza("default", protocol.Stanza, xmlns=xmlns)

	def registerStanza(self, tagName, stanza, xmlns=None, order="info"):
		""" Used to declare some top-level stanza name to dispatcher.
		   Needed to start registering handlers for such stanzas.
		   Iq, Message and Presence stanzas are registered by default. 
		"""
		if not xmlns:
			xmlns = self._owner.defaultNamespace
		self.printf("Registering %s as %s (%s)" % (tagName, stanza, xmlns), order)
		self.handlers[xmlns][tagName] = {"type": stanza, "default": []}

	def registerHandler(self, name, handler, htype="", namespace="", xmlns=None):
		"""	Register user callback as stanzas handler of declared type. Callback must take
			arguments: dispatcher instance (for replying), incomed return of previous handlers.
			The callback must raise xmpp.protocol.NodeProcessed just before return if it want preven
			callbacks to be called with the same stanza as argument _and_, more importantly
			library from returning stanza to sender with error set (to be enabled in 0.2 ve
			Arguments:
				"name" - name of stanza. F.e. "iq".
				"handler" - user callback.
				"htype" - value of stanza"s "type" attribute. If not specified any value match
				"namespace" - namespace of child that stanza must contain.
		"""
		if not xmlns:
			xmlns = self._owner.defaultNamespace
		self.printf("Registering %s for %s type: %s, namespace: %s (%s)" % (handler, name, htype, namespace, xmlns))
		if not htype and not namespace:
			htype = "default"
		if xmlns not in self.handlers:
			self.registerNamespace(xmlns, "warn")
		if name not in self.handlers[xmlns]:
			self.registerStanza(name, protocol.Stanza, xmlns, "warn")
		key = htype + namespace
		if key not in self.handlers[xmlns][name]:
			self.handlers[xmlns][name][key] = []
		self.handlers[xmlns][name][key].append(handler)

	def unregisterHandler(self, name, handler, htype="", namespace="", xmlns=None):
		""" Unregister handler. "htype" and "namespace" must be specified 
			exactly the same as with registering.
		"""
		if not xmlns:
			xmlns = self._owner.defaultNamespace
		self.printf("Unregistering handler %s for %s type: %s, namespace: %s (%s)" % (handler, name, htype, namespace, xmlns), "stop")
		if xmlns not in self.handlers:
			return
		if not htype and not namespace:
			htype = "default"
		key = htype + namespace
		if handler in self.handlers[xmlns][name][key]:
			self.handlers[xmlns][name][key].remove(handler)
			if not self.handlers[xmlns][name][key]:
				del self.handlers[xmlns][name]

	def streamErrorHandler(self, conn, error):
		name, text = "error", error.getData()
		for tag in error.getChildren():
			if tag.getNamespace() == protocol.NS_XMPP_STREAMS:
				if tag.getName() == "text":
					text = tag.getData()
				else:
					name = tag.getName()
		if name in protocol.streamExceptions:
			exc = protocol.streamExceptions[name]
		else:
			exc = StreamError
		raise exc(name, text)

	def dispatch(self, stanza, session=None):
		""" Main procedure that performs XMPP stanza recognition and calling 
			apppropriate handlers for it. Called internally.
		"""
		if not session:
			session = self
		session.Stream._mini_dom = None
		name = stanza.getName()
		if name == "features":
			session.Stream.features = stanza

		xmlns = stanza.getNamespace()
		if xmlns not in self.handlers:
			self.printf("Unknown namespace: %s" % (xmlns), "warn")
			xmlns = "default"
		if name not in self.handlers[xmlns]:
			self.printf("Unknown stanza: %s" % (name), "warn")
			name = "default"
		else:
			self.printf("Got %s/%s stanza" % (xmlns, name), "ok")

		if isinstance(stanza, protocol.Node):
			stanza = self.handlers[xmlns][name]["type"](node=stanza)

		stanzaType = stanza.getType()
		stanzaID = stanza.getID()
		if not stanzaType: 
			stanzaType = ""
		stanzaProps = stanza.getProperties()
		session.printf("Dispatching %s stanza with type: %s, props: %s, id: %s" % (name, stanzaType, stanzaProps, stanzaID))

		if stanzaID in session._expected:
			if isinstance(session._expected[stanzaID], tuple):
				function, args = session._expected[stanzaID]
				del self._expected[stanzaID]
				session.printf("Expected stanza arrived. Callback %s (%s) found!" % (function, args), "ok")
				try:
					function(stanza, *args)
				except(protocol.NodeProcessed):
					pass
			else:
				session.printf("Expected stanza arrived!", "ok")
				session._expected[stanzaID] = stanza
		else:
			handlerList = ["default"]
			if stanzaType in self.handlers[xmlns][name]:
				handlerList.append(stanzaType)
			for prop in stanzaProps:
				if prop in self.handlers[xmlns][name]:
					handlerList.append(prop)
				if stanzaType and (stanzaType + prop) in self.handlers[xmlns][name]:
					handlerList.append(stanzaType + prop)

			chain = self.handlers[xmlns]["default"]["default"]
			for key in handlerList:
				if key:
					chain = chain + self.handlers[xmlns][name][key]
			for handler in chain:
				try:
					handler(session, stanza)
				except protocol.NodeProcessed:
					return

	def waitForResponse(self, id, timeout=DEFAULT_TIMEOUT):
		""" Block and wait until stanza with specific "id" attribute will come.
			If no such stanza is arrived within timeout, return None.
		"""
		self._expected[id] = None
		abortTime = time.time() + timeout
		self.printf("Waiting for ID %s with timeout %s..." % (id, timeout))
		while not self._expected[id]:
			if not self.process(0.1):
				return None 
			if time.time() > abortTime:
				return None 
		response = self._expected[id]
		del self._expected[id]
		return response 

	def sendAndWaitForResponse(self, stanza, timeout=DEFAULT_TIMEOUT):
		""" Put stanza on the wire and wait for recipient's response to it.
		"""
		return self.waitForResponse(self.send(stanza), timeout)

	def sendAndCallForResponse(self, stanza, func, args=None):
		""" Put stanza on the wire and call back when recipient replies.
			Additional callback arguments can be specified in args.
		"""
		if not args:
			args = {}
		self._expected[self.send(stanza)] = (func, args)

	def send(self, stanza):
		""" Serialise stanza and put it on the wire. Assign an unique ID to it before send.
			Returns assigned ID.
		"""
		if isinstance(stanza, basestring):
			return self._owner_send(stanza)
		if not isinstance(stanza, protocol.Stanza): 
			stanzaID = None
		elif not stanza.getID():
			global gID
			gID += 1
			stanzaID = str(gID)
			stanza.setID(stanzaID)
		else:
			stanzaID = stanza.getID()
		stanza.setNamespace(self._owner.Namespace)
		self._owner_send(stanza)
		return stanzaID

	def disconnect(self):
		""" Send a stream terminator and and handle all incoming stanzas 
			before stream closure.
		"""
		self._owner_send("</stream:stream>")
		while self.process(1):
			pass
