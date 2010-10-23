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
		
def processSubscriptions(stanza, conference, nick, trueJid):
	jid = stanza.getFrom().getStripped()
	prsType = stanza.getType()
	if(protocol.PRS_SUBSCRIBE == prsType):
		gRoster.authorize(jid)
		gRoster.subscribe(jid)
	elif(protocol.PRS_UNSUBSCRIBE == prsType):
		gRoster.unauthorize(jid)
		gRoster.delItem(jid)

registerPresenceHandler(processSubscriptions, ROSTER)
