# coding: utf-8;

# attention.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def attentionListener(stanza, msgType, jid, resource, trueJid, body):
	if(stanza.getTags('attention')):
		sendMsg(msgType, jid, resource, u'эй, чочо надо?');

registerMessageHandler(attentionListener, ROSTER);
