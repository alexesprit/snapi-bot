# coding: utf-8

# botstatus.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def setDefBotStatusValue(conference):
	if not getConferenceConfigKey(conference, "show"):
		setConferenceConfigKey(conference, "show", u"online")
		setConferenceConfigKey(conference, "status", None)

def manageBotStatusValue(msgType, conference, nick, param):
	args = param.split(None, 1)
	show, status = "", ""
	if args[0] in STATUS_STRINGS:
		show = args[0]
		if len(args) > 1:
			status = args[1]
	else:
		status = param
	setConferenceStatus(conference, status, show)
	
	setConferenceConfigKey(conference, "status", status)
	setConferenceConfigKey(conference, "show", show)
	saveConferenceConfig(conference)
	
	sendMsg(msgType, conference, nick, u"Запомнила")

registerEvent(setDefBotStatusValue, ADDCONF)
registerCommand(manageBotStatusValue, u"ботстатус", 30, 
				u"Меняет статус бота", 
				u"<[статус] [текст]>", 
				(u"away", u"away сплю"), 
				CHAT | PARAM)
