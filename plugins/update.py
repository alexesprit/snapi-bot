# coding: utf-8

# update.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def updateWorkingCopy(msgType, conference, nick, param):
	response = os.popen("svn up").read()
	if response:
		currentRev = Version.revision
		newRev = os.popen("svnversion -n").read()
		if currentRev != newRev:
			sendMsg(msgType, conference, nick, u"Обновлено до редакции %s" % (newRev))
			setOfflineStatus(u"Выключаюсь... (Обновление)")
			shutdown(True)
		else:
			sendMsg(msgType, conference, nick, u"Ваша копия не требует обновления")
	else:
		sendMsg(msgType, conference, nick, u"Не удалось обновиться, возможно не установлена SubVersion")

registerCommand(updateWorkingCopy, u"update", 100,
				u"Обновление рабочей копии бота",
				None,
				None,
				CMD_ANY | CMD_NONPARAM)
