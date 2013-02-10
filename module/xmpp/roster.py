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
		self._owner.registerHandler("iq", self._parseIQ, protocol.NS_ROSTER)

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
		for item in stanza.getQueryNode().getTags("item"):
			jid = item.getAttr("jid")
			name = item.getAttr("name")
			subsc = item.getAttr("subscription")
			self.rosterData[jid] = (name, subsc)
			self.printf("Setting roster item %s" % (jid), "ok")
		self.state = ROSTER_LOADED

	def getName(self, jid):
		""" Returns name of jid.
		"""
		return self.rosterData[jid][0]

	def getSubscription(self, jid):
		""" Returns "subscription" value of jid. """
		return self.rosterData[jid][1]

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
		iq.setQueryPayload([protocol.Node("item", {"jid": jid, "subscription": "remove"})])
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
