# transports.py

# Copyright (C) 2003-2004 Alexey "Snake" Nezhdanov

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# $Id: transports.py,v 1.35 2009/04/07 08:34:09 snakeru Exp $

"""
	This module contains the low-level implementations of xmpppy connect methods or
	(in other words) transports for xmpp-stanzas.
	Currently here is three transports:
	direct TCP connect - TCPSocket class
	proxied TCP connect - HTTPProxySocket class (CONNECT proxies)
	TLS connection - TLS class. Can be used for SSL connections also.

	Transports are stackable so you - f.e. TLS use HTPPROXYsocket or TCPSocket 
	as more low-level transport.
"""

import base64
import select
import socket
import sys

isPython26 = sys.version[:3] == '2.6'

if isPython26:
	import ssl

import dispatcher
import plugin
import protocol

from utils.utils import ustr

BUFLEN = 1024

DBG_PROXY = "proxy"
DBG_SOCKET = "socket"
DBG_TLS = "tls"

TLS_SUCCESS = 0x1
TLS_FAILURE = 0x2
TLS_UNSUPPORTED = 0x3

class TCPSocket(plugin.PlugIn):
	""" This class defines direct TCP connection method. """
	def __init__(self, server=None, useResolver=True):
		""" Cache connection point 'server'. 'server' is the tuple of (host,  port)
			absolutely the same as standard tcp socket uses. However library will lookup for 
			('_xmpp-client._tcp.' + host) SRV record in DNS and connect to the found (if it is)
			server instead
		"""
		plugin.PlugIn.__init__(self)
		self.debugFlag = DBG_SOCKET
		self._exportedMethods = (self.send, self.disconnect)
		self._server, self.useResolver = server, useResolver

	def lookup(self, server):
		" SRV resolver. Takes server=(host, port) as argument. Returns new (host, port) pair "
		import dns
		host, port  =  server
		query = '_xmpp-client._tcp.%s' % (host)
		# ensure we haven't cached an old configuration
		dns.DiscoverNameServers()
		response = dns.DnsRequest().req(query, qtype='SRV')
		if response.answers:
			port, host = response.answers[0]['data'][2:4]
			port = int(port)
			server = (host, port)
		return server

	def plugin(self, owner):
		""" Fire up connection. Return non-empty string on success.
			Also registers self.disconnected method in the owner's dispatcher.
			Called internally.
		"""
		if not self._server:
			self._server = (self._owner.Server, 5222)
		if self.useResolver:
			server = self.lookup(self._server)
		else:
			server = self._server
		if not self.connect(server):
			return
		self._owner.Connection = self
		return 'ok'

	def getHost(self):
		""" Return the 'host' value that is connection is [will be] made to."""
		return self._server[0]

	def getPort(self):
		""" Return the 'port' value that is connection is [will be] made to."""
		return self._server[1]

	def connect(self, server=None):
		""" Try to connect to the given host/port. Does not lookup for SRV record.
			Returns non-empty string on success. """
		try:
			if not server:
				server = self._server
			self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self._sock.connect((server[0], int(server[1])))
			self._send = self._sock.sendall
			self._recv = self._sock.recv
			self.printf("Successfully connected to remote host %s:%s" % (server[0], server[1]), "ok")
			return 'ok'
		except socket.error, (errno, strerror): 
			self.printf("Failed to connect to remote host %s: %s (%s)" % (server[0], strerror, errno), 'error')
		except Exception:
			pass

	def plugout(self):
		""" Disconnect from the remote server and unregister self.disconnected method from
			the owner's dispatcher. """
		self._sock.close()
		if hasattr(self._owner, 'Connection'):
			del self._owner.Connection

	def receive(self):
		""" Reads all pending incoming data.
			In case of disconnection calls owner's disconnected() method and then raises IOError exception."""
		try:
			received = self._recv(BUFLEN)
		except socket.sslerror, e:
			self._seen_data = 0
			if e[0] == socket.SSL_ERROR_WANT_READ:
				return ''
			if e[0] == socket.SSL_ERROR_WANT_WRITE:
				return ''
			self.printf('Socket error while receiving data', 'error')
			sys.exc_clear()
			self._owner.disconnected()
			raise IOError("Disconnected from server")
		except Exception:
			received = ''

		while self.pending_data(0):
			try:
				add = self._recv(BUFLEN)
			except Exception:
				add = ""
			received += add
			if not add:
				break

		if len(received): # length of 0 means disconnect
			self._seen_data = 1
			self.printf(received, 'got')
		else:
			self.printf('Socket error while receiving data', 'error')
			self._owner.disconnected()
			raise IOError("Disconnected from server")
		return received

	def send(self, rawData):
		""" Writes raw outgoing data. Blocks until done.
			If supplied data is unicode string, encodes it to utf-8 before send."""
		if(isinstance(rawData, unicode)):
			rawData = rawData.encode('utf-8')
		elif(not isinstance(rawData, str)):
			rawData = ustr(rawData).encode('utf-8')
		try:
			self._send(rawData)
			# Avoid printing messages that are empty keepalive packets.
			if rawData.strip():
				self.printf(rawData, 'sent')
		except Exception:
			self.printf("Socket error while sending data", 'error')
			self._owner.disconnected()

	def pending_data(self, timeout=0):
		""" Returns true if there is a data ready to be read. """
		return select.select([self._sock], [], [], timeout)[0]

	def disconnect(self):
		""" Closes the socket. """
		self.printf("Closing socket", 'stop')
		self._sock.close()

class HTTPProxySocket(TCPSocket):
	""" HTTP (CONNECT) proxy connection class. Uses TCPSocket as the base class
		redefines only connect method. Allows to use HTTP proxies like squid with
		(optionally) simple authentication (using login and password). """
	def __init__(self, proxy, server, useResolver=True):
		""" Caches proxy and target addresses.
			'proxy' argument is a dictionary with mandatory keys 'host' and 'port' (proxy address)
			and optional keys 'user' and 'password' to use for authentication.
			'server' argument is a tuple of host and port - just like TCPSocket uses. """
		TCPSocket.__init__(self, server, useResolver)
		self.debugFlag = DBG_PROXY
		self._proxy = proxy

	def plugin(self, owner):
		""" Starts connection. Used interally. Returns non-empty string on success."""
		owner.printfFlags.append(DBG_CONNECT_PROXY)
		return TCPSocket.plugin(self, owner)

	def connect(self):
		""" Starts connection. Connects to proxy, supplies login and password to it
			(if were specified while creating instance). Instructs proxy to make
			connection to the target server. Returns non-empty sting on success. """
		if not TCPSocket.connect(self, (self._proxy['host'], self._proxy['port'])):
			return
		self.printf("Proxy server contacted, performing authentification", 'start')
		connector = ['CONNECT %s:%s HTTP/1.0' % (self._server), 
			'Proxy-Connection: Keep-Alive', 
			'Pragma: no-cache', 
			'Host: %s:%s' % (self._server), 
			'User-Agent: HTTPProxySocket/v0.1']
		if('name' in self._proxy and 'password' in self._proxy):
			credentials = '%(user)s:%(password)s' % (self._proxy)
			credentials = base64.encodestring(credentials).strip()
			connector.append('Proxy-Authorization: Basic %s' % (credentials))
		connector.append('\r\n')
		self.send('\r\n'.join(connector))
		try:
			reply = self.receive().replace('\r', '')
		except IOError:
			self.printf('Proxy suddenly disconnected', 'error')
			self._owner.disconnected()
			return
		try:
			proto, code, desc = reply.split('\n')[0].split(' ', 2)
		except Exception:
			raise ValueError('Invalid proxy reply')
		if code != '200':
			self.printf('Invalid proxy reply: %s %s %s'%(proto, code, desc), 'error')
			self._owner.disconnected()
			return
		while reply.find('\n\n') ==  -1:
			try:
				reply +=  self.receive().replace('\r', '')
			except IOError:
				self.printf('Proxy suddenly disconnected', 'error')
				self._owner.disconnected()
				return
		self.printf("Authentification successfull. Jabber server contacted.", 'ok')
		return 'ok'

	def printf(self, text, severity):
		"""Overwrites printf tag to allow printf output be presented as "CONNECTproxy"."""
		return self._owner.printf(DBG_CONNECT_PROXY, text, severity)

class TLS(plugin.PlugIn):
	""" TLS connection used to encrypts already estabilished tcp connection."""
	def PlugIn(self, owner, forceSSL=False):
		""" If the 'startSSL' argument is true then starts using encryption immidiatedly.
			If 'startSSL' is false then starts encryption as soon as TLS feature is
			declared by the server (if it were already declared - it is ok).
		"""
		# Already enabled
		if hasattr(owner, 'TLS'):
			return
		self.debugFlag = DBG_TLS
		plugin.PlugIn.PlugIn(self, owner)
		self.forceSSL = forceSSL
		if forceSSL:
			return self._startSSL()
		self.state = None
		self.featuresHandler(self._owner.Dispatcher, self._owner.Dispatcher.Stream.features)

	def plugout(self):
		""" Unregisters TLS handler's from owner's dispatcher. """
		if not self.forceSSL:
			self._owner.unregisterHandler("proceed", self.startTLSHandler, xmlns=protocol.NS_TLS)
			self._owner.unregisterHandler("failure", self.startTLSHandler, xmlns=protocol.NS_TLS)

	def featuresHandler(self, conn, feats):
		""" Used to analyse server <features/> tag for TLS support.
			If TLS is supported starts the encryption negotiation. Used internally
		"""
		if not feats.getTag("starttls", namespace=protocol.NS_TLS):
			self.state = TLS_UNSUPPORTED
			self.printf("TLS unsupported by remote server", 'warn')
			return
		self.printf("TLS supported by remote server. Requesting TLS start", 'ok')
		self._owner.registerHandler("proceed", self.startTLSHandler, xmlns=protocol.NS_TLS)
		self._owner.registerHandler("failure", self.startTLSHandler, xmlns=protocol.NS_TLS)
		self._owner.Connection.send("<starttls xmlns=\"%s\"/>" % (protocol.NS_TLS))

	def pending_data(self, timeout=0):
		""" Returns true if there possible is a data ready to be read. """
		return self._tcpsock._seen_data or select.select([self._tcpsock._sock], [], [], timeout)[0]

	def _startSSL(self):
		tcpsock = self._owner.Connection
		if isPython26:
			tcpsock._sslObj = ssl.wrap_socket(tcpsock._sock, None, None)
		else:
			tcpsock._sslObj = socket.ssl(tcpsock._sock, None, None)
			tcpsock._sslIssuer = tcpsock._sslObj.issuer()
			tcpsock._sslServer = tcpsock._sslObj.server()
		tcpsock._recv = tcpsock._sslObj.read
		tcpsock._send = tcpsock._sslObj.write
		tcpsock._seen_data = 1
		self._tcpsock = tcpsock
		tcpsock.pending_data = self.pending_data
		tcpsock._sock.setblocking(0)

		self.state = TLS_SUCCESS

	def startTLSHandler(self, conn, stanza):
		""" Handle server reply if TLS is allowed to process. Behaves accordingly.
			Used internally.
		"""
		if stanza.getName() == "failure":
			self.state = TLS_FAILURE
			self.printf("Got starttls response: %s" % (self.state), "error")
			return
		self.state = TLS_SUCCESS
		self.printf("Got starttls proceed response. Switching to TLS/SSL...", "ok")
		self._startSSL()
		self._owner.Dispatcher.PlugOut()
		dispatcher.Dispatcher().PlugIn(self._owner)