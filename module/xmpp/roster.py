# roster.py

# Copyright (C) 2003-2005 Alexey "Snake" Nezhdanov

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# $Id: roster.py,v 1.20 2005/07/13 13:22:52 snakeru Exp $

"""
	Simple roster implementation. Can be used though for different tasks like
	mass-renaming of contacts.
"""

import plugin
import protocol

DBG_ROSTER = "roster"

ROSTER_EMPTY = 0x0
ROSTER_LOADED = 0x1

class Roster(plugin.PlugIn):
	""" Defines a plenty of methods that will allow you to manage roster.
		Also automatically track presences from remote jids taking into 
		account that every jid can have multiple resources connected. Does not
		currently support "error" presences.
		You can also use mapping interface for access to the internal representation of
		contacts in roster.
	"""
	def __init__(self):
		""" Init internal variables.
		"""
		plugin.PlugIn.__init__(self)
		self._exportedMethods = (self.getRoster, )

		self.debugFlag = DBG_ROSTER
		self.state = ROSTER_EMPTY
		self.rosterData = {}

	def plugin(self):
		""" Register presence and subscription trackers in the owner's dispatcher.
			Also request roster from server if the "request" argument is set.
			Used internally.
		"""
		self._owner.registerHandler("iq", self._parseIQ, namespace=protocol.NS_ROSTER)
		self._owner.registerHandler("presence", self._parsePresence)

	def getRoster(self):
		""" Requests roster from server if neccessary and returns self.
		"""
		if self.state == ROSTER_EMPTY:
			self._requestRoster()
		while self.state != ROSTER_LOADED:
			self._owner.process(1)
		return self

	def _requestRoster(self):
		""" Request roster from server if it were not yet requested 
			(or if the "force" argument is set).
		"""
		self._owner.send(protocol.Iq(protocol.TYPE_GET, protocol.NS_ROSTER))
		self.printf("Roster requested from server", "start")

	def _parseIQ(self, stanza):
		""" Subscription tracker. Used internally for setting items state 
			in internal roster representation.
		"""
		for item in stanza.getTag("query").getTags("item"):
			jid = item.getAttr("jid")
			if item.getAttr("subscription") == "remove":
				if jid in self.rosterData:
					del self.rosterData[jid]
					return
			if not jid in self.rosterData:
				self.rosterData[jid] = {}
			self.rosterData[jid]["name"] = item.getAttr("name")
			self.rosterData[jid]["subscription"] = item.getAttr("subscription")
			self.rosterData[jid]["groups"] = []
			if "resources" not in self.rosterData[jid]:
				self.rosterData[jid]["resources"] = {}
			for group in item.getTags("group"):
				self.rosterData[jid]["groups"].append(group.getData())
			self.printf("Setting roster item %s" % (jid), "ok")
		self.state = ROSTER_LOADED

	def _parsePresence(self, stanza):
		""" Presence tracker. Used internally for setting items' resources state
			in internal roster representation.
		"""
		fulljid = stanza.getFrom()
		barejid = fulljid.getBareJID()
		if barejid in self.rosterData:
			prsType = stanza.getType()
			resource = fulljid.getResource()
			item = self.rosterData[barejid]
			if not prsType:
				self.printf("Setting roster item %s for resource %s" % (barejid, resource), "ok")
				show = stanza.getShow()
				status = stanza.getStatus()
				priority = stanza.getPriority() or "0"
				item["resources"][resource] = {"show": show, "status": status, "priority": int(priority)}
			elif prsType == "unavailable":
				if resource in item["resources"]:
					del item["resources"][resource]

	def _getItemData(self, jid, field):
		""" Return specific jid's representation in internal format. 
			Used internally.
		"""
		jid = protocol.UserJID(jid).getBareJID()
		return self.rosterData[jid][field]

	def _getResourceData(self, jid, field):
		""" Return specific jid's resource representation in internal format. 
			Used internally.
		"""
		fulljid = protocol.UserJID(jid)
		barejid = fulljid.getBareJID()
		resource = fulljid.getResource()
		if resource:
			if resource in self.rosterData[barejid]["resources"]:
				return self.rosterData[barejid]["resources"][resource][field]
		elif self.rosterData[barejid]["resources"]:
			lastPriority = -129
			resources = self.rosterData[barejid]["resources"]
			for r in resources:
				priority = resources[r]["priority"]
				if priority > lastPriority:
					resource, lastPriority = r, priority
			return resources[resource][field]

	def getGroups(self, jid):
		""" Returns groups list that jid belongs to.
		"""
		return self._getItemData(jid, "groups")

	def getName(self, jid):
		""" Returns name of jid.
		"""
		return self._getItemData(jid, "name")

	def getPriority(self, jid):
		""" Returns priority of jid. JID should be a full (not bare).
		"""
		return self._getResourceData(jid, "priority")

	def getShow(self, jid):
		""" Returns "show" value of jid. JID should be a full (not bare).
		"""
		return self._getResourceData(jid, "show")

	def getStatus(self, jid):
		""" Returns "status" value of jid. JID should be a full (not bare).
		"""
		return self._getResourceData(jid, "status")

	def getSubscription(self, jid):
		""" Returns "subscription" value of jid. """
		return self._getItemData(jid, "subscription")

	def getResources(self, jid):
		""" Returns list of connected resources of jid.
		"""
		fulljid = protocol.UserJID(jid)
		barejid = fulljid.getBareJID()
		return self.rosterData[barejid]["resources"].keys()

	def setItem(self, jid, name=None, groups=None):
		""" Creates/renames jid and sets the groups list that it now belongs to.
		"""
		iq = Iq("set", NS_ROSTER)
		query = iq.getTag("query")
		if name:
			attrs["name"] = name
		item = query.setTag("item", attrs={"jid": jid})
		if not groups:
			groups = []
		for group in groups: 
			item.addChild(node=Node("group", payload=[group]))
		self._owner.send(iq)

	def keys(self):
		""" Provided for the sake of dictionary interface.
		"""
		return self.rosterData.keys()

	def getItem(self, item):
		""" Get the contact in the internal format
			or None if jid is not in roster.
		"""
		if item in self.rosterData:
			return self.rosterData[item]

	def delItem(self, jid):
		""" Delete jid from roster.
		"""
		iq = protocol.Iq(protocol.TYPE_SET, protocol.NS_ROSTER)
		query = iq.getTag("query")
		itemNode = protocol.Node("item", {"jid": jid, "subscription": "remove"})
		query.addChild(node=itemNode)
		self._owner.send(iq)
		
	def subscribe(self, jid):
		""" Send subscription request to jid.
		"""
		prs = protocol.Presence(jid, protocol.PRS_SUBSCRIBE)
		self._owner.send(prs)

	def unsubscribe(self, jid):
		""" Ask for removing our subscription for jid.
		"""
		prs = protocol.Presence(jid, protocol.PRS_UNSUBSCRIBE)
		self._owner.send(prs)

	def authorize(self, jid):
		""" Authorise jid. Works only if these jid requested auth previously.
		"""
		prs = protocol.Presence(jid, protocol.PRS_SUBSCRIBED)
		self._owner.send(prs)

	def unauthorize(self, jid):
		""" Unauthorise jid. Use for declining authorisation request 
			or for removing existing authorization.
		"""
		prs = protocol.Presence(jid, protocol.PRS_UNSUBSCRIBED)
		self._owner.send(prs)
