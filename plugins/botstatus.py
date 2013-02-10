# coding: utf-8

# botstatus.py
# Initial Copyright (с) ???
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def setDefaultBotStatusValue(conference):
	if not getConferenceConfigKey(conference, "show"):
		setConferenceConfigKey(conference, "show", u"online")
		setConferenceConfigKey(conference, "status", None)

def manageBotStatusValue(msgType, conference, nick, param):
	args = param.split(None, 1)
	show, status = None, None

	if args[0] in STATUS_STRINGS:
		show = args[0]
		if len(args) > 1:
			status = args[1]
	else:
		status = param
	setStatus(conference, show, status)
	
	setConferenceConfigKey(conference, "status", status)
	setConferenceConfigKey(conference, "show", show)
	saveConferenceConfig(conference)
	
	sendMsg(msgType, conference, nick, u"Запомнила")

registerEventHandler(setDefaultBotStatusValue, EVT_ADDCONFERENCE)

registerCommand(manageBotStatusValue, u"ботстатус", 30, 
				u"Устанавливает статус бота",
				u"<[статус] [текст]>", 
				(u"away", u"away сплю"), 
				CMD_CONFERENCE | CMD_PARAM)
