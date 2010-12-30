# coding: utf-8

# invite.py
# Initial Copyright (c) 2008 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def sendInvite(msgType, conference, nick, param):
	param = param.split(None, 1)
	user = param[0]
	if not isJID(user):
		if isNickInConference(conference, user):
			truejid = getTrueJID(conference, user)
		else:
			sendMsg(msgType, conference, nick, u"А кто это?")
			return
	else:
		truejid = user
	reason = (len(param) == 2) and param[1] or None
	msg = protocol.Message(to=conference)
	x = protocol.Node("x")
	x.setNamespace(protocol.NS_MUC_USER)
	inv = x.addChild("invite", {"to": truejid})
	if reason:
		inv.setTagData("reason", reason)
	else:
		inv.setTagData("reason", u"Вас приглашает %s" % (nick))
	msg.addChild(node=x)
	gClient.send(msg)
	sendMsg(msgType, conference, nick, u"Кинула инвайт")
			
registerCommand(sendInvite, u"призвать", 10, 
				u"Приглашет заданного пользователя в конференцию", 
				u"<ник|жид> [причина]", 
				(u"Nick", u"user@server.tld есть дело"), 
				CMD_CONFERENCE | CMD_PARAM)
