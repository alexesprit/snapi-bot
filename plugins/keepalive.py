# coding: utf-8;

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

KEEP_ID = 'keep_id';
KEEPALIVE_TIMEOUT = 300;

def _sendKeepAlivePacket(stanza, keepID, conference):
	if(keepID == stanza.getID()):
		if(ERROR == stanza.getType()):
			if(stanza.getErrorCode() == '503'):
				startTimer(REJOIN_TIMEOUT, joinConference, (conference, getBotNick(conference), getChatKey(conference, 'password')));
	
def sendKeepAlivePacket():
	for conference in getConferences():
		iq = xmpp.Iq('get');
		keepID = getUniqueID(KEEP_ID);
		iq.setID(keepID);
		iq.addChild('ping', {}, [], xmpp.NS_PING);
		iq.setTo(conference + '/' + getBotNick(conference));
		gClient.SendAndCallForResponse(iq, _sendKeepAlivePacket, (keepID, conference, ));
	startKeepAliveTimer();

def startKeepAliveTimer():
	startTimer(KEEPALIVE_TIMEOUT, sendKeepAlivePacket);

#registerEvent(sendKeepAlivePacket, INIT_2);
