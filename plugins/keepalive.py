# coding: utf-8

# keepalive.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

KEEPALIVE_TIMEOUT = 300

def _sendKeepAlivePacket(stanza, conference):
	if protocol.TYPE_ERROR == stanza.getType():
		if stanza.getErrorCode() == "503":
			startTimer(REJOIN_DELAY, joinConference, (conference, getBotNick(conference), getChatKey(conference, "password")))
	
def sendKeepAlivePacket():
	for conference in getConferences():
		iq = protocol.Iq(protocol.TYPE_GET)
		iq.setID(getUniqueID("keep_id"))
		iq.addChild("ping", {}, [], protocol.NS_PING)
		iq.setTo(conference + "/" + getBotNick(conference))
		gClient.sendAndCallForResponse(iq, _sendKeepAlivePacket, (conference, ))
	startKeepAliveTimer()

def startKeepAliveTimer():
	startTimer(KEEPALIVE_TIMEOUT, sendKeepAlivePacket)

registerEvent(startKeepAliveTimer, INIT_2)
