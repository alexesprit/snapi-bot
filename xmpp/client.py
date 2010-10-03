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

import debug
import socket

debug.Debug.colors['socket'] = debug.colorDarkGray
debug.Debug.colors['proxy'] = debug.colorDarkGray
debug.Debug.colors['dispatcher'] = debug.colorGreen
debug.Debug.colors['roster'] = debug.colorMagenta
debug.Debug.colors['auth'] = debug.colorYellow
debug.Debug.colors['bind'] = debug.colorBrown

debug.Debug.colors['ok'] = debug.colorBrown
debug.Debug.colors['warn'] = debug.colorYellow
debug.Debug.colors['error'] = debug.colorRed
debug.Debug.colors['start'] = debug.colorDarkGray
debug.Debug.colors['stop'] = debug.colorDarkGray
debug.Debug.colors['sent'] = debug.colorYellow
debug.Debug.colors['got'] = debug.colorBrightCyan

SSL_AUTO = 0x0
SSL_FORCE = 0x1
SSL_DISABLE = 0x2

C_TCP = "TCP"
C_TLS = "TLS"
C_SSL = "SSL"

import auth
import dispatcher
import roster
import transports

class CommonClient:
	""" Base for Client and Component classes."""
	def __init__(self, server, port=5222, debugFlags=None):
		""" Caches server name and (optionally) port to connect to. "printf" parameter specifies
			the printf IDs that will go into printf output. You can either specifiy an "include"
			or "exclude" list. The latter is done via adding "always" pseudo-ID to the list.
		"""
		self.Namespace = dispatcher.NS_CLIENT
		self.defaultNamespace = self.Namespace
		self.disconnectHandlers = []
		self.Server = server
		self.Port = port
		self._debug = debug.Debug(debugFlags, validateFlags=False, welcomeMsg=False, prefix='', showFlags=False)
		self.printf = self._debug.show
		self.debugFlags = self._debug.debugFlags
		self._owner = self
		self._registeredName = None
		self.connected = False

	def RegisterDisconnectHandler(self, handler):
		""" Register handler that will be called on disconnect."""
		self.disconnectHandlers.append(handler)

	def UnregisterDisconnectHandler(self, handler):
		""" Unregister handler that is called on disconnect."""
		self.disconnectHandlers.remove(handler)

	def disconnected(self):
		""" Called on disconnection. Calls disconnect handlers and cleans things up. """
		self.connected = False
		for instance in self.disconnectHandlers:
			instance()
		if hasattr(self, C_TLS):
			self.TLS.PlugOut()

	def isConnected(self):
		""" Returns connection state. F.e.: None / 'tls' / 'tcp+non_sasl' . """
		return self.connected

	def connect(self, server=None, proxy=None, SSLMode=False, useResolver=True):
		""" Make a tcp/ip connection, protect it with tls/ssl if possible and start XMPP stream.
			Returns None or C_TCP or C_TLS, depending on the result."""
		if not server:
			server = (self.Server, self.Port)
		if proxy:
			sock = transports.HTTPProxySocket(proxy, server, useResolver)
		else:
			sock = transports.TCPSocket(server, useResolver)
		connected = sock.PlugIn(self)
		if not connected: 
			sock.PlugOut()
			return False
		self._Server, self._Proxy = server, proxy
		self.connected = C_TCP
		if (SSLMode == SSL_AUTO and self.Connection.getPort() in (5223, 443)) or SSLMode == SSL_FORCE:
			try:			   # FIXME. This should be done in transports.py
				transports.TLS().PlugIn(self, startSSL=True)
				self.connected = C_SSL
			except socket.sslerror:
				pass
		dispatcher.Dispatcher().PlugIn(self)
		while self.Dispatcher.Stream._document_attrs is None:
			if not self.Process(1):
				return False
		# If we get version 1.0 stream the features tag MUST BE presented
		if(self.Dispatcher.Stream._document_attrs.get('version') == '1.0'):
			while not self.Dispatcher.Stream.features and self.Process(1):
				pass	  
		return self.connected

class Client(CommonClient):
	""" Example client class, based on CommonClient. """
	def connect(self, server=None, proxy=None, SSLMode=SSL_DISABLE, useResolver=True):
		""" Connect to jabber server. If you want to specify different ip/port to connect to you can
			pass it as tuple as first parameter. If there is HTTP proxy between you and server 
			specify it's address and credentials (if needed) in the second argument.
			If you want ssl/tls support to be discovered and enable automatically, set third argument as SSL_AUTO. (ssl will be autodetected only if port is 5223 or 443)
			If you want to force SSL start (i.e. if port 5223 or 443 is remapped to some non-standard port) then set it to SSL_FORCE.
			If you want to disable tls/ssl support completely, set it to SSL_DISABLE.
			Example: connect(('192.168.5.5', 5222), {'host':'proxy.my.net', 'port':8080, 'user':'me', 'password':'secret'})
			Returns '' or 'TCP' or 'TLS', depending on the result.
		"""
		if(not CommonClient.connect(self, server, proxy, SSLMode, useResolver)):
			return False
		if(SSLMode != SSL_DISABLE and not hasattr(self, C_TLS)):
			transports.TLS().PlugIn(self)
			if(self.Dispatcher.Stream._document_attrs.get('version') == '1.0'):
				# If we get version 1.0 stream the features tag MUST BE presented
				while not self.Dispatcher.Stream.features and self.Process(1):
					pass
				# TLS not supported by server
				if not self.Dispatcher.Stream.features.getTag('starttls'):
					self.TLS.PlugOut()
					return self.connected
				while not self.TLS.starttls and self.Process(1):
					pass
				if self.TLS.starttls != 'success':
					self.TLS.PlugOut()
					return self.connected
				self.connected = C_TLS
		return self.connected

	def auth(self, user, password, resource=None):
		""" Authenticate connnection and bind resource. If resource is not provided
			random one or library name used.
		"""
		self._User, self._Password, self._Resource = user, password, resource
		while not self.Dispatcher.Stream._document_attrs and self.Process(1):
			pass
		# If we get version 1.0 stream the features tag MUST BE presented
		if(self.Dispatcher.Stream._document_attrs.get('version') == '1.0'):
			while not self.Dispatcher.Stream.features and self.Process(1):
				pass
		auth.SASL(user, password).PlugIn(self)
		self.SASL.auth()
		while auth.AUTH_WAITING == self.SASL.state and self.Process(1):
			pass
		if auth.AUTH_SUCCESS == self.SASL.state:
			self.SASL.PlugOut()
			auth.Bind().PlugIn(self)
			if auth.BIND_SUCCESS == self.Bind.Bind(resource):
				self.Bind.PlugOut()
				return auth.AUTH_SUCCESS
		else:
			self.SASL.PlugOut()
			return auth.AUTH_FAILURE

	def getCapsNode(self):
		caps = dispatcher.Node("c")
		caps.setNamespace(dispatcher.NS_CAPS)
		caps.setAttr("node", "http://jimm.net.ru/caps")
		caps.setAttr("ver", "Nz009boXYEIrmRWk1N/Vsw==")
		caps.setAttr("hash", "md5")
		return(caps)

	def getRoster(self):
		""" Return the Roster instance, previously plugging it in and
			requesting roster from server if needed. """
		if(not hasattr(self, 'Roster')):
			roster.Roster().PlugIn(self)
		return self.Roster.getRoster()

	def setStatus(self, show, status, priority):
		prs = dispatcher.Presence(priority=priority)
		if(status):
			prs.setStatus(status)
		if(show):
			prs.setShow(show)
		prs.addChild(node=self.getCapsNode())
		self.send(prs)
