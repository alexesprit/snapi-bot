# coding: utf-8

# invite.py
# Initial Copyright (c) 2008 Als <Als@exploit.in>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def sendInvite(msgType, conference, nick, param):
	args = param.split(None, 1)
	userNick = args[0]
	truejid = getTrueJID(conference, userNick)
	if not truejid:
		if netutil.isJID(userNick):
			truejid = userNick
		else:
			sendMsg(msgType, conference, nick, u"А это кто?")
			return
	reason = (len(args) == 2) and args[1] or None
	msg = protocol.Message(to=conference)
	x = msg.addChild("x", xmlns=protocol.NS_MUC_USER)
	inv = x.addChild("invite", {"to": truejid})
	if not reason:
		reason = u"Вас приглашает %s" % (nick)
	inv.setTagData("reason", reason)
	gClient.send(msg)
	sendMsg(msgType, conference, nick, u"Кинула инвайт")
			
registerCommand(sendInvite, u"призвать", 10, 
				u"Приглашет указанного пользователя в конференцию",
				u"<ник|жид> [причина]", 
				(u"Nick", u"user@server.tld есть дело"), 
				CMD_CONFERENCE | CMD_PARAM)
