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

from plugin import PlugIn
from protocol import Iq, Node, Presence, UserJid
from protocol import TYPE_GET, TYPE_SET, NS_ROSTER

DBG_ROSTER = "roster"

ROSTER_EMPTY = 0x0
ROSTER_REQUESTING = 0x1
ROSTER_LOADED = 0x2

class Roster(PlugIn):
	""" Defines a plenty of methods that will allow you to manage roster.
		Also automatically track presences from remote jids taking into 
		account that every jid can have multiple resources connected. Does not
		currently support 'error' presences.
		You can also use mapping interface for access to the internal representation of
		contacts in roster.
	"""
	def __init__(self):
		""" Init internal variables. """
		PlugIn.__init__(self)
		self.debugFlag = DBG_ROSTER
		self.rosterData = {}
		self.state = ROSTER_EMPTY
		self._exportedMethods = [self.getRoster]

	def plugin(self, owner):
		""" Register presence and subscription trackers in the owner's dispatcher.
			Also request roster from server if the 'request' argument is set.
			Used internally.
		"""
		self._owner.registerHandler("iq", self.rosterIqHandler, namespace=NS_ROSTER)
		self._owner.registerHandler('presence', self.presenceHandler)

	def requestRoster(self):
		""" Request roster from server if it were not yet requested 
			(or if the 'force' argument is set).
		"""
		if(self.state == ROSTER_LOADED):
			return
		self.state = ROSTER_REQUESTING
		self._owner.send(Iq(TYPE_GET, NS_ROSTER))
		self.printf('Roster requested from server', 'start')

	def getRoster(self):
		""" Requests roster from server if neccessary and returns self. """
		if(self.state == ROSTER_EMPTY):
			self.requestRoster()
		while(not self.state == ROSTER_LOADED):
			self._owner.process(10)
		return(self)

	def rosterIqHandler(self, dis, stanza):
		""" Subscription tracker. Used internally for setting items state in
			internal roster representation.
		"""
		for item in stanza.getTag('query').getTags('item'):
			jid = item.getAttr('jid')
			if(item.getAttr('subscription') == 'remove'):
				if(jid in self.rosterData):
					del(self.rosterData[jid])
					return
			self.printf('Setting roster item %s' % (jid), 'ok')
			if(not jid in self.rosterData):
				self.rosterData[jid] = {}
			self.rosterData[jid]['name'] = item.getAttr('name')
			self.rosterData[jid]['ask'] = item.getAttr('ask')
			self.rosterData[jid]['subscription'] = item.getAttr('subscription')
			self.rosterData[jid]['groups'] = []
			if(not 'resources' in self.rosterData[jid]):
				self.rosterData[jid]['resources'] = {}
			for group in item.getTags('group'):
				self.rosterData[jid]['groups'].append(group.getData())
		self.state = ROSTER_LOADED

	def presenceHandler(self, dis, stanza):
		""" Presence tracker. Used internally for setting items' resources state in
			internal roster representation.
		"""
		fullJid = UserJid(stanza.getFrom())
		bareJid = fullJid.getStripped()
		if(bareJid in self.rosterData):
			prsType = stanza.getType()
			resource = fullJid.getResource()
			item = self.rosterData[bareJid]
			if(not prsType):
				self.printf('Setting roster item %s for resource %s' % (bareJid, resource), 'ok')
				show = stanza.getShow()
				status = stanza.getStatus()
				priority = stanza.getPriority() or '0'
				item['resources'][resource] = {'show': show, 'status': status, 'priority': int(priority)}
			elif(prsType == 'unavailable'):
				if(resource in item['resources']):
					del(item['resources'][resource])

	def _getItemData(self, jid, field):
		""" Return specific jid's representation in internal format. Used internally. """
		jid = UserJid(jid).getStripped()
		return(self.rosterData[jid][field])

	def _getResourceData(self, jid, field):
		""" Return specific jid's resource representation in internal format. Used internally. """
		fullJid = UserJid(jid)
		bareJid = fullJid.getStripped()
		resource = fullJid.getResource()
		if(resource):
			if(resource in self.rosterData[bareJid]['resources']):
				return(self.rosterData[bareJid]['resources'][resource][field])
		elif(self.rosterData[bareJid]['resources'].keys()):
			lastPriority = -129
			resources = self.rosterData[bareJid]['resources']
			for r in resources:
				priority = resources[r]['priority']
				if(priority > lastPriority):
					resource, lastpri = r, priority
			return(resources[resource][field])

	def getAsk(self,jid):
		""" Returns 'ask' value of contact 'jid'. """
		return self._getItemData(jid, 'ask')

	def getGroups(self, jid):
		""" Returns groups list that contact 'jid' belongs to. """
		return self._getItemData(jid, 'groups')

	def getName(self, jid):
		""" Returns name of contact 'jid'. """
		return self._getItemData(jid, 'name')

	def getPriority(self, jid):
		""" Returns priority of contact 'jid'. 'jid' should be a full (not bare) UserJid."""
		return self._getResourceData(jid, 'priority')

	def getRawRoster(self):
		""" Returns roster representation in internal format. """
		return(self.rosterData)

	def getRawItem(self, jid):
		""" Returns roster item 'jid' representation in internal format. """
		fullJid = UserJid(jid)
		bareJid = fullJid.getStripped()
		return(self.rosterData[bareJid])

	def getShow(self, jid):
		""" Returns 'show' value of contact 'jid'. 'jid' should be a full (not bare) UserJid. """
		return(self._getResourceData(jid, 'show'))

	def getStatus(self, jid):
		""" Returns 'status' value of contact 'jid'. 'jid' should be a full (not bare) UserJid. """
		return(self._getResourceData(jid, 'status'))

	def getSubscription(self, jid):
		""" Returns 'subscription' value of contact 'jid'. """
		return(self._getItemData(jid, 'subscription'))

	def getResources(self, jid):
		""" Returns list of connected resources of contact 'jid'."""
		fullJid = UserJid(jid)
		bareJid = fullJid.getStripped()
		return(self.rosterData[bareJid]['resources'].keys())

	def setItem(self, jid, name = None, groups = []):
		""" Creates/renames contact 'jid' and sets the groups list that it now belongs to. """
		iq = Iq('set', NS_ROSTER)
		query = iq.getTag('query')
		attrs = {'jid': jid}
		if(name):
			attrs['name'] = name
		item = query.setTag('item', attrs)
		for group in groups: 
			item.addChild(node=Node('group', payload = [group]))
		self._owner.send(iq)

	def getItems(self):
		""" Return list of all [bare] UserJids that the roster is currently tracks. """
		return(self.rosterData.keys())

	def keys(self):
		""" Same as getItems. Provided for the sake of dictionary interface. """
		return(self.rosterData.keys())

	def __getitem__(self, item):
		""" Get the contact in the internal format. Raises KeyError if UserJid 'item' is not in roster. """
		return(self.rosterData[item])

	def getItem(self, item):
		""" Get the contact in the internal format (or None if UserJid 'item' is not in roster). """
		if(item in self.rosterData):
			return(self.rosterData[item])

	def delItem(self, jid):
		""" Delete contact 'jid' from roster. """
		self._owner.send(Iq(TYPE_SET, NS_ROSTER, payload=[Node('item', {'jid': jid,'subscription': 'remove'})]))
		
	def subscribe(self, jid):
		""" Send subscription request to UserJid 'jid'. """
		self._owner.send(Presence(jid, PRS_SUBSCRIBE))

	def unsubscribe(self, jid):
		""" Ask for removing our subscription for UserJid 'jid'. """
		self._owner.send(Presence(jid, PRS_UNSUBSCRIBE))

	def authorize(self, jid):
		""" Authorise UserJid 'jid'. Works only if these UserJid requested auth previously. """
		self._owner.send(Presence(jid, PRS_SUBSCRIBED))

	def unauthorize(self, jid):
		""" Unauthorise UserJid 'jid'. Use for declining authorisation request 
			or for removing existing authorization.
		"""
		self._owner.send(Presence(jid, PRS_UNSUBSCRIBED))
