# simplexml.py based on Mattew Allum's xmlstream.py

# Copyright (C) 2003-2005 Alexey "Snake" Nezhdanov

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# $Id: simplexml.py,v 1.34 2009/03/03 10:24:02 normanr Exp $

""" Simplexml module provides xmpppy library with all needed tools to handle XML nodes and XML streams.
	I'm personally using it in many other separate projects. It is designed to be as standalone as possible.
"""

import xml.parsers.expat
from module.netutil import escapeXML, ustr

class Node(object):
	""" Node class describes syntax of separate XML Node. It have a constructor that permits node creation
		from set of "namespace name", attributes and payload of text strings and other nodes.
		It does not natively support building node from text string and uses NodeBuilder class for that purpose.
		After creation node can be mangled in many ways so it can be completely changed.
		Also node can be serialised into string in one of two modes: default (where the textual representation
		of node describes it exactly) and "fancy" - with whitespace added to make indentation and thus make
		result more readable by human.
	"""

	def __init__(self, name=None, attrs=None, nsp=None, parent=None, node_built=False, node=None):
		""" Takes "tag" argument as the name of node (prepended by namespace, if needed and separated from it
			by a space), attrs dictionary as the set of arguments and "parent" argument that is another node
			that this one will be the child of. Also the __init__ can be provided with "node" argument that is
			either a text string containing exactly one node or another Node instance to begin with. If both
			"node" and other arguments is provided then the node initially created as replica of "node"
			provided and then modified to be compliant with other arguments.
		"""
		if node:
			if not isinstance(node, Node):
				node = NodeBuilder(node, self)
				node_built = True
			else:
				self.name = node.getName()
				self.xmlns = node.getXMLNS()
				self.attrs = node.getAttrs()
				self.data = node.getData()
				self.children = node.getChildren()
				self.parent = node.getParent()
				self.nsd = {}
				for k, v in node.nsd.items():
					self.nsd[k] = v
		else:
			self.name = "tag"
			self.xmlns = ""
			self.attrs = {}
			self.data = None
			self.children = []
			self.parent = None
			self.nsd = {}
		if parent:
			self.parent = parent
		self.nsp_cache = {}
		if nsp:
			for k, v in nsp.items():
				self.nsp_cache[k] = v
		if not attrs:
			attrs = {}
		for attr, val in attrs.items():
			if attr == "xmlns":
				self.nsd[u""] = val
			elif attr.startswith("xmlns:"):
				self.nsd[attr[6:]] = val
			self.attrs[attr] = attrs[attr]
		if name:
			if node_built:
				pfx, self.name = ([""] + name.split(":"))[-2:]
				self.xmlns = self.lookup_nsp(pfx)
			else:
				if " " in name:
					self.xmlns, self.name = name.split()
				else:
					self.name = name

	def lookup_nsp(self, pfx=""):
		ns = self.nsd.get(pfx)
		if ns is None:
			ns = self.nsp_cache.get(pfx)
			if ns is None:
				if self.parent:
					ns = self.parent.lookup_nsp(pfx)
					self.nsp_cache[pfx] = ns
				else:
					return "http://www.gajim.org/xmlns/undeclared"
		return ns

	def __str__(self):
		""" Method used to dump node into textual representation.
		"""
		s = "<" + self.name
		if self.xmlns:
			if not self.parent or self.parent.xmlns != self.xmlns:
				if "xmlns" not in self.attrs:
					s = s + " xmlns=\"%s\"" % (self.xmlns)
		for key in self.attrs.keys():
			val = ustr(self.attrs[key])
			s = s + " %s=\"%s\"" % (key, escapeXML(val))
		if not self.children and not self.data:
			s += " />"
		else:
			s = s + ">"
			if self.children:
				for child in self.children:
					if child:
						s += ustr(child)
			if self.data:
				s += escapeXML(self.getData().strip())
			s += "</%s>" % (self.name)
		return s

	def addChild(self, name=None, attrs=None, xmlns=None, node=None):
		""" If "node" argument is provided, adds it as child node. Else creates new node from
			the other arguments" values and adds it as well.
		"""
		if node:
			newnode = node
			node.parent = self
		else:
			newnode = Node(name=name, parent=self, attrs=attrs)
		if xmlns:
			newnode.setXMLNS(xmlns)
		self.children.append(newnode)
		return newnode

	def getChildren(self):
		""" Returns all node's child nodes as list.
		"""
		return self.children

	def getFirstChild(self):
		if self.children:
			return self.children[0]

	def getAttrs(self):
		""" Returns all node's attributes as dictionary.
		"""
		return self.attrs

	def getAttr(self, attr):
		""" Returns value of specified attribute.
		"""
		return self.attrs.get(attr)
		
	def hasAttr(self, attr):
		""" Checks if node have attribute.
		"""
		return attr in self.attrs

	def setAttr(self, attr, val):
		""" Sets attribute "key" with the value.
		"""
		self.attrs[attr] = val

	def getData(self):
		""" Returns all node CDATA as string (concatenated).
		"""
		return self.data

	def setData(self, data):
		""" Sets node's CDATA to provided string. Resets all previous CDATA!
		"""
		self.data = ustr(data)

	def getName(self):
		""" Returns the name of node.
		"""
		return self.name

	def setName(self, name):
		""" Changes the node name.
		"""
		self.name = name

	def getXMLNS(self):
		""" Returns the namespace of node.
		"""
		return self.xmlns

	def setXMLNS(self, xmlns):
		""" Changes the node namespace.
		"""
		self.xmlns = xmlns

	def getParent(self):
		""" Returns the parent of node (if present).
		"""
		return self.parent

	def setParent(self, node):
		""" Sets node's parent to "node". WARNING: do not checks if the parent already present
			and not removes the node from the list of childs of previous parent.
		"""
		self.parent = node

	def setPayload(self, payload):
		""" Sets node payload according to the list specified. WARNING: completely replaces all node's
			previous content. If you wish just to add child or CDATA - use addData or addChild methods.
		"""
		if isinstance(payload, basestring):
			payload = [payload]
		for i in payload:
			if isinstance(i, Node):
				self.addChild(node=i)
			else:
				self.setData(i)

	def getTag(self, name, attrs=None, xmlns=None):
		""" Filters all child nodes using specified arguments as filter.
			Returns the first found or None if not found.
		"""
		return self.getTags(name, attrs, xmlns, one=True)

	def setTag(self, name, attrs=None, xmlns=None):
		""" Same as getTag but if the node with specified namespace/attributes not found, creates such
			node and returns it.
		"""
		node = self.getTag(name, attrs, xmlns=xmlns)
		if node:
			return node
		else:
			return self.addChild(name, attrs, xmlns=xmlns)

	def getTagAttr(self, name, attr):
		""" Returns attribute value of the child with specified name
			or None if no such attribute.
		"""
		try:
			return self.getTag(name).attrs[attr]
		except (AttributeError, KeyError):
			return None

	def setTagAttr(self, name, attr, val):
		""" Creates new node (if not already present) with name "name"
			and sets it's attribute "attr" to value "val".
		"""
		try:
			self.getTag(name).attrs[attr] = val
		except AttributeError:
			self.addChild(name, attrs={attr: val})

	def getTagData(self, name):
		""" Returns cocatenated CDATA of the child with specified name.
		"""
		try:
			return self.getTag(name).getData()
		except AttributeError:
			return None

	def setTagData(self, name, val, attrs=None):
		""" Creates new node (if not already present) with name "name" and (optionally) attributes "attrs"
			and sets it's CDATA to string "val".
		"""
		try:
			self.getTag(name, attrs).setData(val)
		except AttributeError:
			self.addChild(name, attrs).setData(val)

	def getTags(self, name, attrs=None, xmlns=None, one=False):
		""" Filters all child nodes using specified arguments as filter.
			Returns the list of nodes found.
		"""
		nodes = []
		if not attrs:
			attrs = {}
		for node in self.children:
			if not node:
				continue
			if xmlns and xmlns != node.getXMLNS():
				continue
			if node.getName() == name:
				for key in attrs:
					if key not in node.attrs or node.attrs[key] != attrs[key]:
						break
				else:
					nodes.append(node)
			if one and nodes:
				return nodes[0]
		if not one:
			return nodes

class NodeBuilder:
	""" Builds a Node class minidom from data parsed to it. This class used for two purposes:
		1. Creation an XML Node from a textual representation. F.e. reading a config file. See an XML2Node method.
		2. Handling an incoming XML stream. This is done by mangling
		   the __dispatch_depth parameter and redefining the dispatch method.
		You do not need to use this class directly if you do not designing your own XML handler.
	"""
	def __init__(self, data=None):
		""" Takes two optional parameters: "data" and "initial_node".
			By default class initialised with empty Node class instance.
			Though, if "initial_node" is provided it used as "starting point".
			You can think about it as of "node upgrade".
			"data" (if provided) feeded to parser immidiatedly after instance init.
		"""
		self._parser = xml.parsers.expat.ParserCreate()
		self._parser.StartElementHandler = self.starttag
		self._parser.EndElementHandler = self.endtag
		self._parser.CharacterDataHandler = self.handle_cdata
		self._parser.buffer_text = True
		self.parse = self._parser.Parse

		self.__depth = 0
		self.__last_depth = 0
		self._dispatch_depth = 1
		self._document_attrs = None
		self._document_nsp = None
		self._mini_dom = None
		self.data_buffer = []
		self._ptr = None
		if data:
			self._parser.Parse(data,1)

	def destroy(self):
		""" Method used to allow class instance to be garbage-collected.
		"""
		self._parser.StartElementHandler = None
		self._parser.EndElementHandler = None
		self._parser.CharacterDataHandler = None

	def starttag(self, name, attrs):
		""" XML Parser callback. Used internally.
		"""
		self.__depth += 1
		if self.__depth == self._dispatch_depth:
			if not self._mini_dom :
				self._mini_dom = Node(name=name, attrs=attrs, nsp=self._document_nsp, node_built=True)
			else:
				Node(self._mini_dom, name=name, attrs=attrs, nsp=self._document_nsp, node_built=True)
			self._ptr = self._mini_dom
		elif self.__depth > self._dispatch_depth:
			self._ptr.children.append(Node(name=name, parent=self._ptr, attrs=attrs, node_built=True))
			self._ptr = self._ptr.children[-1]
		if self.__depth == 1:
			self._document_attrs = {}
			self._document_nsp = {}
			nsp, name = ([""]+name.split(":"))[-2:]
			for attr, val in attrs.items():
				if attr == "xmlns":
					self._document_nsp[u""] = val
				elif attr.startswith("xmlns:"):
					self._document_nsp[attr[6:]] = val
				else:
					self._document_attrs[attr] = val
			xmlns = self._document_nsp.get(nsp, "http://www.gajim.org/xmlns/undeclared-root")
			try:
				self.stream_header_received(name, attrs, xmlns)
			except ValueError, e:
				self._document_attrs = None
				raise ValueError(str(e))

	def endtag(self, tag):
		""" XML Parser callback. Used internally.
		"""
		self._ptr.setData("".join(self.data_buffer))
		self.data_buffer = []
		if self.__depth == self._dispatch_depth:
			self.dispatch(self._mini_dom)
		elif self.__depth > self._dispatch_depth:
			self._ptr = self._ptr.parent
		self.__depth -= 1

	def handle_cdata(self, data):
		""" XML Parser callback. Used internally.
		"""
		self.data_buffer.append(data)

	def getDom(self):
		""" Returns just built Node.
		"""
		return self._mini_dom

	def dispatch(self, stanza):
		""" Gets called when the NodeBuilder reaches some level of depth on it's way up with the built
			node as argument. Can be redefined to convert incoming XML stanzas to program events.
		"""

	def stream_header_received(self, name, attrs, xmlns):
		""" Method called when stream just opened.
		"""

def XML2Node(xml):
	""" Converts supplied textual string into XML node. Handy f.e. for reading configuration file.
		Raises xml.parser.expat.parsererror if provided string is not well-formed XML.
	"""
	return NodeBuilder(xml).getDom()
