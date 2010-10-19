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
from utils.utils import escapeXML, ustr

class Node(object):
	""" Node class describes syntax of separate XML Node. It have a constructor that permits node creation
		from set of "namespace name", attributes and payload of text strings and other nodes.
		It does not natively support building node from text string and uses NodeBuilder class for that purpose.
		After creation node can be mangled in many ways so it can be completely changed.
		Also node can be serialised into string in one of two modes: default (where the textual representation
		of node describes it exactly) and "fancy" - with whitespace added to make indentation and thus make
		result more readable by human.
	"""

	def __init__(self, tag=None, attrs=None, payload=None, parent=None, nsp=None, node_built=False, node=None):
		""" Takes "tag" argument as the name of node (prepended by namespace, if needed and separated from it
			by a space), attrs dictionary as the set of arguments, payload list as the set of textual strings
			and child nodes that this node carries within itself and "parent" argument that is another node
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
				self.name = node.name
				self.namespace = node.namespace
				self.attrs = node.getAttrs()
				self.data = node.getData()
				self.children = node.getChildren()
				self.parent = node.parent
				self.nsd = {}
				for k, v in node.nsd.items():
					self.nsd[k] = v
		else:
			self.name = 'tag'
			self.namespace = ''
			self.attrs = {}
			self.data = []
			self.children = []
			self.parent = None
			self.nsd = {}
		if parent:
			self.parent = parent
		self.nsp_cache = {}
		if nsp:
			for k, v in nsp.items():
				self.nsp_cache[k] = v
		if(not attrs):
			attrs = {}
		for attr, val in attrs.items():
			if attr == 'xmlns':
				self.nsd[u''] = val
			elif attr.startswith('xmlns:'):
				self.nsd[attr[6:]] = val
			self.attrs[attr]=attrs[attr]
		if tag:
			if node_built:
				pfx, self.name = ([''] + tag.split(':'))[-2:]
				self.namespace = self.lookup_nsp(pfx)
			else:
				if ' ' in tag:
					self.namespace,self.name = tag.split()
				else:
					self.name = tag
		if(not payload):
			payload = []
		if isinstance(payload, basestring):
			payload = [payload]
		for i in payload:
			if isinstance(i, Node):
				self.addChild(node=i)
			else:
				self.data.append(ustr(i))

	def lookup_nsp(self, pfx=''):
		ns = self.nsd.get(pfx)
		if ns is None:
			ns = self.nsp_cache.get(pfx)
			if ns is None:
				if self.parent:
					ns = self.parent.lookup_nsp(pfx)
					self.nsp_cache[pfx] = ns
				else:
					return 'http://www.gajim.org/xmlns/undeclared'
		return ns

	def __str__(self):
		""" Method used to dump node into textual representation. """
		s = "<" + self.name
		if self.namespace:
			if not self.parent or self.parent.namespace != self.namespace:
				if 'xmlns' not in self.attrs:
					s = s + ' xmlns="%s"' % (self.namespace)
		for key in self.attrs.keys():
			val = ustr(self.attrs[key])
			s = s + ' %s="%s"' % (key, escapeXML(val))
		s = s + ">"
		if self.children:
			for child in self.children:
				if child:
					s += ustr(child)
		if self.data:
			s += escapeXML(self.getData().strip())
		if not self.children and not self.data:
			s = s[:-1] + " />"
		else:
			s += "</%s>" % (self.name)
		return s

	def addChild(self, name=None, attrs=None, payload=None, namespace=None, node=None):
		""" If "node" argument is provided, adds it as child node. Else creates new node from
			the other arguments' values and adds it as well."""
		if node:
			newnode = node
			node.parent = self
		else:
			newnode = Node(tag=name, parent=self, attrs=attrs, payload=payload)
		if namespace:
			newnode.setNamespace(namespace)
		self.children.append(newnode)
		return newnode

	def addData(self, data):
		""" Adds some CDATA to node. """
		self.data.append(ustr(data))

	def clearData(self):
		""" Removes all CDATA from the node. """
		self.data = []

	def delAttr(self, key):
		""" Deletes an attribute "key" """
		del self.attrs[key]

	def delChild(self, node, attrs=None):
		""" Deletes the "node" from the node's childs list, if "node" is an instance.
			Else deletes the first node that have specified name and (optionally) attributes.
		"""
		if not isinstance(node, Node):
			node = self.getTag(node,attrs)
		del self.children[self.children.index(node)]
		return node

	def getAttrs(self):
		""" Returns all node's attributes as dictionary. """
		return self.attrs

	def getAttr(self, key):
		""" Returns value of specified attribute. """
		return self.attrs.get(key)

	def getChildren(self):
		""" Returns all node's child nodes as list. """
		return self.children

	def getFirstChild(self):
		if self.children:
			return self.children[0]

	def getData(self):
		""" Returns all node CDATA as string (concatenated). """
		return ''.join(self.data)

	def getName(self):
		""" Returns the name of node """
		return self.name

	def getNamespace(self):
		""" Returns the namespace of node """
		return self.namespace

	def getParent(self):
		""" Returns the parent of node (if present). """
		return self.parent

	def getPayload(self):
		""" Return the payload of node i.e. list of child nodes and CDATA entries.
			F.e. for "<node>text1<nodea/><nodeb/> text2</node>" will be returned list:
			['text1', <nodea instance>, <nodeb instance>, ' text2'].
		"""
		ret = []
		for i in range(max(len(self.data),len(self.children))):
			if i < len(self.data) and self.data[i]:
				ret.append(self.data[i])
			if i < len(self.children) and self.children[i]:
				ret.append(self.children[i])
		return ret

	def getTag(self, name, attrs=None, namespace=None): 
		""" Filters all child nodes using specified arguments as filter.
			Returns the first found or None if not found.
		"""
		return self.getTags(name, attrs, namespace, one=True)

	def getTagAttr(self,tag,attr):
		""" Returns attribute value of the child with specified name (or None if no such attribute)."""
		try:
			return self.getTag(tag).attrs[attr]
		except(AttributeError, KeyError):
			return None

	def getTagData(self,tag):
		""" Returns cocatenated CDATA of the child with specified name."""
		try:
			return self.getTag(tag).getData()
		except(AttributeError):
			return None

	def getTags(self, name, attrs=None, namespace=None, one=False):
		""" Filters all child nodes using specified arguments as filter.
			Returns the list of nodes found.
		"""
		nodes=[]
		if not attrs:
			attrs = {}
		for node in self.children:
			if not node:
				continue
			if namespace and namespace!=node.getNamespace():
				continue
			if node.getName() == name:
				for key in attrs:
				   if key not in node.attrs or \
						node.attrs[key] != attrs[key]:
					break
				else:
					nodes.append(node)
			if one and nodes:
				return nodes[0]
		if not one:
			return nodes

	def iterTags(self, name, attrs=None, namespace=None):
		""" Iterate over all children using specified arguments as filter. """
		if not attrs:
			attrs = {}
		for node in self.children:
			if not node:
				continue
			if namespace is not None and namespace != node.getNamespace():
				continue
			if node.getName() == name:
				for key in attrs:
					if key not in node.attrs or \
						node.attrs[key]!=attrs[key]:
							break
				else:
					yield node

	def setAttr(self, key, val):
		""" Sets attribute "key" with the value "val". """
		self.attrs[key] = val

	def setData(self, data):
		""" Sets node's CDATA to provided string. Resets all previous CDATA!"""
		self.data = [ustr(data)]

	def setName(self,val):
		""" Changes the node name. """
		self.name = val

	def setNamespace(self, namespace):
		""" Changes the node namespace. """
		self.namespace=namespace

	def setParent(self, node):
		""" Sets node's parent to "node". WARNING: do not checks if the parent already present
			and not removes the node from the list of childs of previous parent.
		"""
		self.parent = node

	def setPayload(self, payload, add=0):
		""" Sets node payload according to the list specified. WARNING: completely replaces all node's
			previous content. If you wish just to add child or CDATA - use addData or addChild methods.
		"""
		if isinstance(payload, basestring):
			payload = [payload]
		if add:
			self.children += payload
		else:
			self.children = payload

	def setTag(self, name, attrs=None, namespace=None):
		""" Same as getTag but if the node with specified namespace/attributes not found, creates such
			node and returns it.
		"""
		node = self.getTags(name, attrs, namespace=namespace, one=True)
		if node:
			return node
		else:
			return self.addChild(name, attrs, namespace=namespace)

	def setTagAttr(self, tag, attr, val):
		""" Creates new node (if not already present) with name "tag"
			and sets it's attribute "attr" to value "val".
		"""
		try:
			self.getTag(tag).attrs[attr] = val
		except(AttributeError):
			self.addChild(tag, attrs={attr: val})

	def setTagData(self, tag, val, attrs=None):
		""" Creates new node (if not already present) with name "tag" and (optionally) attributes "attrs"
			and sets it's CDATA to string "val". """
		try:
			self.getTag(tag, attrs).setData(ustr(val))
		except(AttributeError):
			self.addChild(tag, attrs, payload=[ustr(val)])

	def hasAttr(self, key):
		""" Checks if node have attribute "key"."""
		return key in self.attrs

	def __getitem__(self, item):
		""" Returns node's attribute "item" value. """
		return self.getAttr(item)

	def __setitem__(self, item, val):
		""" Sets node's attribute "item" value. """
		return self.setAttr(item,val)

	def __delitem__(self, item):
		""" Deletes node's attribute "item". """
		return self.delAttr(item)

	def __getattr__(self, attr):
		""" Reduce memory usage caused by T/NT classes - use memory only when needed. """
		if attr == 'T':
			self.T = T(self)
			return self.T
		if attr == 'NT':
			self.NT = NT(self)
			return self.NT
		raise AttributeError

class T:
	""" Auxiliary class used to quick access to node's child nodes. """
	def __init__(self, node):
		setattr(self, 'node', node)

	def __getattr__(self, attr):
		return self.node.getTag(attr)

	def __setattr__(self, attr, val):
		if isinstance(val,Node):
			Node.__init__(self.node.setTag(attr), node=val)
		else:
			return self.node.setTagData(attr,val)

	def __delattr__(self, attr):
		return self.node.delChild(attr)

class NT(T):
	""" Auxiliary class used to quick create node's child nodes. """
	def __getattr__(self, attr):
		return self.node.addChild(attr)

	def __setattr__(self, attr, val):
		if isinstance(val, Node):
			self.node.addChild(attr, node=val)
		else:
			return self.node.addChild(attr, payload=[val])

class NodeBuilder:
	""" Builds a Node class minidom from data parsed to it. This class used for two purposes:
		1. Creation an XML Node from a textual representation. F.e. reading a config file. See an XML2Node method.
		2. Handling an incoming XML stream. This is done by mangling
		   the __dispatch_depth parameter and redefining the dispatch method.
		You do not need to use this class directly if you do not designing your own XML handler."""
	def __init__(self, data=None, initial_node=None):
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
		self._parser.StartNamespaceDeclHandler = self.handle_namespace_start
		self._parser.buffer_text = True
		self.Parse = self._parser.Parse

		self.__depth = 0
		self.__last_depth = 0
		self.__max_depth = 0
		self._dispatch_depth = 1
		self._document_attrs = None
		self._document_nsp = None
		self._mini_dom=initial_node
		self.last_is_data = 1
		self._ptr=None
		self.data_buffer = None
		self.streamError = ''
		if data:
			self._parser.Parse(data,1)

	def check_data_buffer(self):
		if self.data_buffer:
			self._ptr.data.append(''.join(self.data_buffer))
			del self.data_buffer[:]
			self.data_buffer = None

	def destroy(self):
		""" Method used to allow class instance to be garbage-collected. """
		self.check_data_buffer()
		self._parser.StartElementHandler = None
		self._parser.EndElementHandler = None
		self._parser.CharacterDataHandler = None
		self._parser.StartNamespaceDeclHandler = None

	def starttag(self, tag, attrs):
		""" XML Parser callback. Used internally """
		self.check_data_buffer()
		self._inc_depth()
		if self.__depth == self._dispatch_depth:
			if not self._mini_dom :
				self._mini_dom = Node(tag=tag, attrs=attrs, nsp=self._document_nsp, node_built=True)
			else:
				Node(self._mini_dom, tag=tag, attrs=attrs, nsp=self._document_nsp, node_built=True)
			self._ptr = self._mini_dom
		elif self.__depth > self._dispatch_depth:
			self._ptr.children.append(Node(tag=tag,parent=self._ptr,attrs=attrs, node_built=True))
			self._ptr = self._ptr.children[-1]
		if self.__depth == 1:
			self._document_attrs = {}
			self._document_nsp = {}
			nsp, name = (['']+tag.split(':'))[-2:]
			for attr, val in attrs.items():
				if attr == 'xmlns':
					self._document_nsp[u''] = val
				elif attr.startswith('xmlns:'):
					self._document_nsp[attr[6:]] = val
				else:
					self._document_attrs[attr] = val
			ns = self._document_nsp.get(nsp, 'http://www.gajim.org/xmlns/undeclared-root')
			try:
				self.stream_header_received(ns, name, attrs)
			except ValueError, e:
				self._document_attrs = None
				raise ValueError(str(e))
		if not self.last_is_data and self._ptr.parent:
			self._ptr.parent.data.append('')
		self.last_is_data = 0

	def endtag(self, tag ):
		""" XML Parser callback. Used internally """
		self.check_data_buffer()
		if self.__depth == self._dispatch_depth:
			if self._mini_dom.getName() == 'error':
				self.streamError = self._mini_dom.getChildren()[0].getName()
			self.dispatch(self._mini_dom)
		elif self.__depth > self._dispatch_depth:
			self._ptr = self._ptr.parent
		self._dec_depth()
		self.last_is_data = 0
		if self.__depth == 0: self.stream_footer_received()

	def handle_cdata(self, data):
		""" XML Parser callback. Used internally """
		if self.last_is_data:
			if self.data_buffer:
				self.data_buffer.append(data)
		elif self._ptr:
			self.data_buffer = [data]
			self.last_is_data = 1

	def handle_namespace_start(self, prefix, uri):
		""" XML Parser callback. Used internally """
		self.check_data_buffer()

	def getDom(self):
		""" Returns just built Node. """
		self.check_data_buffer()
		return self._mini_dom

	def dispatch(self, stanza):
		""" Gets called when the NodeBuilder reaches some level of depth on it's way up with the built
			node as argument. Can be redefined to convert incoming XML stanzas to program events. 
		"""
	def stream_header_received(self,ns,tag,attrs):
		""" Method called when stream just opened. """
		self.check_data_buffer()

	def stream_footer_received(self):
		""" Method called when stream just closed. """
		self.check_data_buffer()

	def has_received_endtag(self, level=0):
		""" Return True if at least one end tag was seen (at level) """
		return self.__depth <= level and self.__max_depth > level

	def _inc_depth(self):
		self.__last_depth = self.__depth
		self.__depth += 1
		self.__max_depth = max(self.__depth, self.__max_depth)

	def _dec_depth(self):
		self.__last_depth = self.__depth
		self.__depth -= 1

def XML2Node(xml):
	""" Converts supplied textual string into XML node. Handy f.e. for reading configuration file.
		Raises xml.parser.expat.parsererror if provided string is not well-formed XML.
	"""
	return NodeBuilder(xml).getDom()
