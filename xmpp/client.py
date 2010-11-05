# client.py

# Copyright (C) 2003-2005 Alexey "Snake" Nezhdanov

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# $Id: client.py, v 1.61 2009/04/07 06:19:42 snakeru Exp $

"""
	Provides PlugIn class functionality to develop extentions for xmpppy.
	Also provides Client class implementations as the
	examples of xmpppy structures usage.
	These classes can be used for simple applications "AS IS" though.
"""

import socket

import auth
import debug
import dispatcher
import protocol
import roster
import transports

SECURE_AUTO = 0x0
SECURE_FORCE = 0x1
SECURE_DISABLE = 0x2

C_TCP = "TCP"
C_TLS = "TLS"
C_SSL = "SSL"

class CommonClient:
	""" Base for Client class."""
	def __init__(self, server, port=5222, debugFlags=None):
		""" Caches server name and (optionally) port to connect to. "debugFlags" parameter specifies
			the debug IDs that will go into debug output. You can either specifiy an "include"
			or "exclude" list. The latter is done via adding "always" pseudo-ID to the list.
		"""
		self.Namespace = protocol.NS_CLIENT
		self.defaultNamespace = self.Namespace
		self.disconnectHandlers = []

		self.Server = server
		self.Port = port

		self._debug = debug.Debug(debugFlags, showFlags=False)
		self.printf = self._debug.show
		self.debugFlags = self._debug.debugFlags
		self.initDebugColors()

		self._owner = self
		self._registeredName = None
		self.connected = False
	
	def initDebugColors(self):
		self._debug.colors["auth"] = debug.colorYellow
		self._debug.colors["bind"] = debug.colorBrown
		self._debug.colors["dispatcher"] = debug.colorGreen
		self._debug.colors["roster"] = debug.colorMagenta
		self._debug.colors["socket"] = debug.colorBrightRed
		self._debug.colors["tls"] = debug.colorBrightRed

		self._debug.colors["ok"] = debug.colorBrightCyan
		self._debug.colors["got"] = debug.colorBlue
		self._debug.colors["sent"] = debug.colorBrown
		self._debug.colors["stop"] = debug.colorDarkGray
		self._debug.colors["warn"] = debug.colorYellow
		self._debug.colors["error"] = debug.colorRed
		self._debug.colors["start"] = debug.colorDarkGray
	
	def registerDisconnectHandler(self, handler):
		""" Register handler that will be called on disconnect.
		"""
		self.disconnectHandlers.append(handler)

	def unregisterDisconnectHandler(self, handler):
		""" Unregister handler that is called on disconnect.
		"""
		self.disconnectHandlers.remove(handler)

	def disconnected(self):
		""" Called on disconnection. Calls disconnect handlers and cleans things up.
		"""
		self.connected = False
		for instance in self.disconnectHandlers:
			instance()
		if hasattr(self, "TLS"):
			self.TLS.PlugOut()

	def isConnected(self):
		""" Returns connection state. F.e.: None, "TCP", "TLS", "SSL".
		"""
		return self.connected

	def connect(self, server=None, SecureMode=SECURE_DISABLE, useResolver=True):
		""" Make a TCP/IP connection, protect it with TLS/SSL if possible and start XMPP stream.
			Returns None, "TCP", "TLS" or "SSL", depending on the result.
		"""
		if not server:
			server = (self.Server, self.Port)
		sock = transports.TCPSocket(server, useResolver)
		connected = sock.PlugIn(self)
		if not connected: 
			sock.PlugOut()
			return False
		self._Server = server
		self.connected = C_TCP
		if (SecureMode == SECURE_AUTO and self.Connection.getPort() in (5223, 443)) or SecureMode == SECURE_FORCE:
			# FIXME. This should be done in transports.py
			try:
				transports.TLS().PlugIn(self, forceSSL=True)
				self.connected = C_SSL
			except socket.sslerror:
				self.TLS.PlugOut()
				return False
		dispatcher.Dispatcher().PlugIn(self)
		while self.Dispatcher.Stream._document_attrs is None:
			if not self.process(1):
				return False
		# If we get version 1.0 stream the features tag MUST BE presented
		if self.Dispatcher.Stream._document_attrs.get("version") == "1.0":
			while not self.Dispatcher.Stream.features and self.process(1):
				pass	  
		return self.connected

class Client(CommonClient):
	""" Example client class, based on CommonClient. """
	def connect(self, server=None, secureMode=SECURE_DISABLE, useResolver=True):
		""" Connect to jabber server. If you want to specify different ip/port to connect to you can
			pass it as tuple as first parameter. If you want TLS/SSL support to be discovered and enable automatically, 
			set third argument as SECURE_AUTO (SSL will be autodetected only if port is 5223 or 443)
			If you want to force SSL start (i.e. if port 5223 or 443 is remapped to some non-standard port) then set it to SECURE_FORCE.
			If you want to disable TLS/SSL support completely, set it to SECURE_DISABLE.
			Returns None or "TCP", "SSL" "TLS", depending on the result.
		"""
		if not CommonClient.connect(self, server, secureMode, useResolver):
			return None
		if secureMode != SECURE_DISABLE and not hasattr(self, C_TLS):
			transports.TLS().PlugIn(self)
			if self.Dispatcher.Stream._document_attrs.get("version") == "1.0":
				# If we get version 1.0 stream the features tag MUST BE presented
				while not self.Dispatcher.Stream.features and self.process(1):
					pass
				if transports.TLS_UNSUPPORTED == self.TLS.state:
					self.TLS.PlugOut()
					return self.connected
				while not self.TLS.state and self.process(1):
					pass
				if self.TLS.state != transports.TLS_SUCCESS:
					self.TLS.PlugOut()
					return False
				self.connected = C_TLS
		return self.connected

	def auth(self, user, password, resource=None):
		""" Authenticate connnection and bind resource. If resource is not provided
			random one or library name used.
		"""
		self._User, self._Password, self._Resource = user, password, resource
		while not self.Dispatcher.Stream._document_attrs and self.process(1):
			pass
		# If we get version 1.0 stream the features tag MUST BE presented
		if self.Dispatcher.Stream._document_attrs.get("version") == "1.0":
			while not self.Dispatcher.Stream.features and self.process(1):
				pass
		auth.SASL(user, password).PlugIn(self)
		self.SASL.auth()
		while auth.AUTH_WAITING == self.SASL.state and self.process(1):
			pass
		if auth.AUTH_SUCCESS == self.SASL.state:
			self.SASL.PlugOut()
			auth.Bind().PlugIn(self)
			if auth.BIND_SUCCESS == self.Bind.bindResource(resource):
				self.Bind.PlugOut()
				return auth.AUTH_SUCCESS
		else:
			self.SASL.PlugOut()
			return auth.AUTH_FAILURE

	def getCapsNode(self):
		caps = protocol.Node("c")
		caps.setNamespace(protocol.NS_CAPS)
		caps.setAttr("node", "http://jimm.net.ru/caps")
		caps.setAttr("ver", "Nz009boXYEIrmRWk1N/Vsw==")
		caps.setAttr("hash", "md5")
		return caps

	def getRoster(self):
		""" Return the Roster instance, previously plugging it in and
			requesting roster from server if needed.
		"""
		if not hasattr(self, "Roster"):
			roster.Roster().PlugIn(self)
		return self.Roster.getRoster()

	def setStatus(self, show, status, priority):
		prs = protocol.Presence(priority=priority)
		if status:
			prs.setStatus(status)
		if show:
			prs.setShow(show)
		prs.addChild(node=self.getCapsNode())
		self.send(prs)
