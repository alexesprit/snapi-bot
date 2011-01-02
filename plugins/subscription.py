# coding: utf-8

# subscription.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
		
def processSubscriptions(stanza, jid, resource):
	prsType = stanza.getType()
	if protocol.PRS_SUBSCRIBE == prsType:
		printf(u"%s has added me into his/her roster" % (jid))
		gRoster.authorize(jid)
		gRoster.subscribe(jid)
	elif protocol.PRS_UNSUBSCRIBE == prsType:
		printf(u"%s has removed me into his/her roster" % (jid))
		gRoster.unauthorize(jid)
		gRoster.delItem(jid)
	elif protocol.PRS_SUBSCRIBED == prsType:
		printf(u"I've added %s into my roster" % (jid), FLAG_SUCCESS)
	elif protocol.PRS_UNSUBSCRIBED == prsType:
		printf(u"I've removed %s from my roster" % (jid), FLAG_SUCCESS)

registerEventHandler(processSubscriptions, EVT_PRS | H_ROSTER)
