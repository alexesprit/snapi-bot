# coding: utf-8

# roster.py
# Initial Copyright (с) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

ROSTERSTATUS_FILE = "rosterstatus.dat"

def setRosterStatus(msgType, conference, nick, param):
	args = param.split(None, 1)
	show, status = None, None

	if args[0] in STATUS_STRINGS:
		show = args[0]
		if len(args) > 1:
			status = args[1]
	else:
		status = param
	setStatus(show, status, Config.PRIORITY)

	path = getConfigPath(ROSTERSTATUS_FILE)
	io.dump(path, {"show": show, "status": status})

	sendMsg(msgType, conference, nick, u"Запомнила")

def updateRosterAndStatus():
	roster = gClient.getRoster()
	counter = 0
	for jid in roster.keys():
		subsc = roster.getSubscription(jid)
		if subsc != "both":
			roster.delItem(jid)
			counter += 1
	if counter:
		printf("%d users were dropped from my roster" % counter)
	path = getConfigPath(ROSTERSTATUS_FILE)
	status = io.load(path)
	if status:
		setStatus(None, status["show"], status["status"])

def showRoster(msgType, conference, nick, param):
	roster = gClient.getRoster()
	elements = [u"%d) %s [%s]" % (i + 1, jid, roster.getSubscription(jid)) 
			for i, jid in enumerate(sorted(roster.keys()))]
	sendMsg(msgType, conference, nick,  u"Смотри, кто у меня есть:\n%s" % ("\n".join(elements)))

registerEventHandler(updateRosterAndStatus, EVT_READY)
registerCommand(showRoster, u"ростер", 100, 
				u"Показывает содержимое ростера", 
				None, 
				None, 
				CMD_ROSTER | CMD_NONPARAM)
registerCommand(setRosterStatus, u"ростерстатус", 100,
				u"Устанавливает статус в ростере",
				u"<[статус] [текст]>",
				(u"away", u"away сплю"),
				CMD_ROSTER | CMD_PARAM)
