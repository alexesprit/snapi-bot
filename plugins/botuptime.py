# coding: utf-8

# botuptime.py
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

def getUsedMemorySize():
	if os.name == "posix":
		pipe = os.popen("ps -o rss -p %s" % os.getpid())
		pipe.readline()
		return float(pipe.readline().strip()) / 1024
	return 0

def showBotUptime(msgType, conference, nick, param):
	buf = []

	uptime = int(time.time() - gInfo["start"])
	buf.append(u"Время работы: %s. " % (getUptimeStr(uptime)))
	buf.append(u"Получено %(msg)d сообщений, %(prs)d презенсов и %(iq)d iq-запросов, выполнено %(cmd)d команд. " % (gInfo))
	memUsage = getUsedMemorySize()
	if memUsage:
		buf.append(u"Используется %0.2f МБ памяти. " % (memUsage))
	buf.append(u"Было запущено %(thr)d потоков, " % (gInfo))
	buf.append(u"в данный момент активно %d потоков. " % (threading.activeCount()))
	if gInfo["err"]:
		buf.append(u"Необработанных ошибок: %(err)d" % (gInfo))
	sendMsg(msgType, conference, nick, "".join(buf))

registerCommand(showBotUptime, u"ботап", 10,
				u"Показывает статистику работы бота",
				None,
				None,
				CMD_ANY | CMD_NONPARAM)
