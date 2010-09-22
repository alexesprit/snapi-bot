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
debug.Debug.colors['xml'] = debug.colorBrown
debug.Debug.colors['client'] = debug.colorCyan
debug.Debug.colors['component'] = debug.colorCyan
debug.Debug.colors['dispatcher'] = debug.colorGreen
debug.Debug.colors['browser'] = debug.colorBlue
debug.Debug.colors['auth'] = debug.colorYellow
debug.Debug.colors['roster'] = debug.colorMagenta
debug.Debug.colors['auth'] = debug.colorYellow

debug.Debug.colors['down'] = debug.colorBrown
debug.Debug.colors['up'] = debug.colorBrown
debug.Debug.colors['data'] = debug.colorBrown
debug.Debug.colors['ok'] = debug.colorGreen
debug.Debug.colors['warn'] = debug.colorYellow
debug.Debug.colors['error'] = debug.colorRed
debug.Debug.colors['start'] = debug.colorDarkGray
debug.Debug.colors['stop'] = debug.colorDarkGray
debug.Debug.colors['sent'] = debug.colorYellow
debug.Debug.colors['got'] = debug.colorBrightCyan

DBG_CLIENT = 'client'

SSL_AUTO = 0x0;
SSL_FORCE = 0x1;
SSL_DISABLE = 0x2;

C_TCP = 'TCP';
C_TLS = 'TLS';
C_SSL = 'SSL';

class PlugIn:
	""" Common xmpppy plugins infrastructure: plugging in/out, printfging. """
	def __init__(self):
		self._exported_methods = []
		self.DBG_LINE = self.__class__.__name__.lower()

	def PlugIn(self, owner):
		""" Attach to main instance and register ourself and all our staff in it. """
		self._owner = owner
		if self.DBG_LINE not in owner.debugFlags:
			owner.debugFlags.append(self.DBG_LINE)
		self.printf('Plugging %s into %s' % (self, self._owner), 'start')
		className = self.__class__.__name__;
		if hasattr(owner, className):
			return self.printf('Plugging ignored: another instance already plugged.', 'error')
		self._old_owners_methods = []
		for method in self._exported_methods:
			methodName = method.__name__
			if hasattr(owner, methodName):
				self._old_owners_methods.append(getattr(owner, methodName))
			setattr(owner, methodName, method)
		setattr(owner, className, self)
		if hasattr(self, 'plugin'):
			return self.plugin(owner)
 
	def PlugOut(self):
		""" Unregister all our staff from main instance and detach from it. """
		self.printf('Plugging %s out of %s.' % (self, self._owner), 'stop')
		ret = None
		if hasattr(self, 'plugout'):
			ret = self.plugout()
		self._owner.debugFlags.remove(self.DBG_LINE)
		for method in self._exported_methods:
			delattr(self._owner, method.__name__)
		for method in self._old_owners_methods:
			setattr(self._owner, method.__name__, method)
		delattr(self._owner, self.__class__.__name__)
		return ret

	def printf(self, text, severity='info'):
		""" Feed a provided printf line to main instance's printf facility along with our ID string. """
		self._owner.printf(text, self.DBG_LINE, severity)

import transports, dispatcher, auth, roster

class CommonClient:
	""" Base for Client and Component classes."""
	def __init__(self, server, port=5222, debugFlags=None):
		""" Caches server name and (optionally) port to connect to. "printf" parameter specifies
			the printf IDs that will go into printf output. You can either specifiy an "include"
			or "exclude" list. The latter is done via adding "always" pseudo-ID to the list.
		"""
		self.Namespace, self.DBG = dispatcher.NS_CLIENT, DBG_CLIENT
		self.defaultNamespace = self.Namespace
		self.disconnectHandlers = []
		self.Server = server
		self.Port = port
		self._debug = debug.Debug(debugFlags, validateFlags=False, welcomeMsg=False, prefix='', showFlags=False)
		self.printf = self._debug.show
		self.debugFlags = self._debug.debugFlags
		self.debugFlags.append(self.DBG)
		self._owner = self
		self._registeredName = None
		self.connected = None
		self._route = 0

	def RegisterDisconnectHandler(self, handler):
		""" Register handler that will be called on disconnect."""
		self.disconnectHandlers.append(handler)

	def UnregisterDisconnectHandler(self, handler):
		""" Unregister handler that is called on disconnect."""
		self.disconnectHandlers.remove(handler)

	def disconnected(self):
		""" Called on disconnection. Calls disconnect handlers and cleans things up. """
		self.connected = None
		self.printf(self.DBG, 'Disconnect detected', 'stop')
		for instance in self.disconnectHandlers:
			instance()
		if hasattr(self, 'TLS'):
			self.TLS.PlugOut()

	def isConnected(self):
		""" Returns connection state. F.e.: None / 'tls' / 'tcp+non_sasl' . """
		return self.connected

	def connect(self, server=None, proxy=None, SSLMode=False, useResolver=True):
		""" Make a tcp/ip connection, protect it with tls/ssl if possible and start XMPP stream.
			Returns None or C_TCP or C_TLS, depending on the result."""
		if not server: server = (self.Server, self.Port)
		if proxy: sock = transports.HTTPPROXYSocket(proxy, server, useResolver)
		else: sock = transports.TCPSocket(server, useResolver)
		connected = sock.PlugIn(self)
		if not connected: 
			sock.PlugOut()
			return
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
				return False;
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
			return False;
		if(SSLMode != SSL_DISABLE and not hasattr(self, C_TLS)):
			transports.TLS().PlugIn(self)
			if(self.Dispatcher.Stream._document_attrs.get('version') == '1.0'):
				# If we get version 1.0 stream the features tag MUST BE presented
				while not self.Dispatcher.Stream.features and self.Process(1):
					pass
				# TLS not supported by server
				if not self.Dispatcher.Stream.features.getTag('starttls'):
					return self.connected
				while not self.TLS.starttls and self.Process(1):
					pass
				if not hasattr(self, C_TLS) or self.TLS.starttls != 'success':
					return self.connected
				self.connected = C_TLS
		return self.connected

	def auth(self, user, password, resource=None, sasl=True):
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
		if sasl:
			auth.SASL(user, password).PlugIn(self)
		if not sasl or self.SASL.startsasl == 'not-supported':
			if not resource:
				resource = 'xmpppy'
			if auth.NonSASL(user, password, resource).PlugIn(self):
				return 'old_auth'
			return
		self.SASL.auth()
		while self.SASL.startsasl == 'in-process' and self.Process(1):
			pass
		if self.SASL.startsasl == 'success':
			auth.Bind().PlugIn(self)
			while self.Bind.bound is None and self.Process(1):
				pass
			self.SASL.PlugOut()
			if self.Bind.Bind(resource):
				return 'sasl'
		else:
			if hasattr(self, 'SASL'):
				self.SASL.PlugOut()

	def getRoster(self):
		""" Return the Roster instance, previously plugging it in and
			requesting roster from server if needed. """
		if(not hasattr(self, 'Roster')):
			roster.Roster().PlugIn(self)
		return self.Roster.getRoster()
