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


"""
	Provides Client class implementations as the examples of xmpppy 
	structures usage.
"""

import socket

import auth
import debug
import dispatcher
import protocol
import roster
import transports

SECURE_DISABLE = 0x0
SECURE_AUTO = 0x1
SECURE_FORCE = 0x2

C_TCP = "TCP"
C_TLS = "TLS"
C_SSL = "SSL"

class Client:
	def __init__(self, server, port=5222, debugFlags=None):
		""" Caches server name and (optionally) port to connect to. "debugFlags" parameter specifies
			the debug IDs that will go into debug output. You can either specifiy an "include"
			or "exclude" list. The latter is done via adding "always" pseudo-ID to the list.
		"""
		self.namespace = protocol.NS_CLIENT
		self.disconnectHandlers = []

		self.server = server
		self.port = port

		self._owner = self
		self.connectType = None

		if not debugFlags:
			debugFlags = []	
		self._initDebugger(debugFlags)
	
	def _initDebugger(self, debugFlags):
		self._debug = debug.Debug(debugFlags, showFlags=False)
		self.printf = self._debug.show
		self.debugFlags = self._debug.debugFlags

		if debugFlags:
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
		self.connectType = None
		for instance in self.disconnectHandlers:
			instance()

	def getConnectType(self):
		return self.connectType

	def isConnected(self):
		""" Returns "True" if connection state is not "None".
		"""
		return self.connectType != None

	def connect(self, secureMode=SECURE_DISABLE, useResolver=True):
		""" Connect to jabber server. If you want TLS/SSL support to be discovered and enable automatically, 
			set third argument as SECURE_AUTO (SSL will be autodetected only if port is 5223 or 443)
			If you want to force SSL start (i.e. if port 5223 or 443 is remapped to some non-standard port) then set it to SECURE_FORCE.
			If you want to disable TLS/SSL support completely, set it to SECURE_DISABLE.
			Returns None or "TCP", "SSL" "TLS", depending on the result.
		"""
		sock = transports.TCPSocket(useResolver)
		connectType = sock.PlugIn(self)
		if not connectType: 
			sock.PlugOut()
			return None
		self.connectType = C_TCP
		isSSLPort = self.port in (5223, 443)
		if (secureMode == SECURE_AUTO and isSSLPort) or secureMode == SECURE_FORCE:
			# FIXME. This should be done in transports.py
			try:
				transports.TLS().PlugIn(self, forceSSL=True)
				self.connectType = C_SSL
			except socket.sslerror:
				self.TLS.PlugOut()
				return None
		dispatcher.Dispatcher().PlugIn(self)
		while self.Dispatcher.stream._document_attrs is None:
			if not self.process(1):
				return None
		# If we get version 1.0 stream the features tag MUST BE presented
		if self.Dispatcher.stream._document_attrs.get("version") == "1.0":
			while not self.Dispatcher.stream.features and self.process(1):
				pass
		if secureMode == SECURE_AUTO and not isSSLPort:
			# If we get version 1.0 stream the features tag MUST BE presented
			if self.Dispatcher.stream._document_attrs.get("version") == "1.0":
				transports.TLS().PlugIn(self)
				if transports.TLS_UNSUPPORTED == self.TLS.state:
					self.TLS.PlugOut()
					return self.connectType
				while not self.TLS.state and self.process(1):
					pass
				if self.TLS.state != transports.TLS_SUCCESS:
					self.TLS.PlugOut()
					return None
				self.connectType = C_TLS
		return self.connectType

	def auth(self, username, password, resource=None):
		""" Authenticate connnection and bind resource. If resource is not provided
			random one or library name used.
		"""
		self.username, self.password, self.resource = username, password, resource
		while not self.Dispatcher.stream._document_attrs and self.process(1):
			pass
		# If we get version 1.0 stream the features tag MUST BE presented
		if self.Dispatcher.stream._document_attrs.get("version") == "1.0":
			while not self.Dispatcher.stream.features and self.process(1):
				pass
		auth.SASL(username, password).PlugIn(self)
		self.SASL.auth()
		while auth.AUTH_WAITING == self.SASL.state and self.process(1):
			pass
		if auth.AUTH_SUCCESS == self.SASL.state:
			self.SASL.PlugOut()
			auth.Bind().PlugIn(self)
			if auth.BIND_SUCCESS == self.Bind.bind(resource):
				self.Bind.PlugOut()
				return True
			else:
				self.Bind.PlugOut()
				return False				
		else:
			self.SASL.PlugOut()
			return False

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
		self.send(prs)
