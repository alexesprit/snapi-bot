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

def showBotUptime(msgType, conference, nick, parameters):
	uptime = int(time.time() - gInfo["start"])
	message = u"Время работы: %s. " % (getUptimeStr(uptime))
	message += u"Получено %(msg)d сообщений, обработано %(prs)d презенсов и %(iq)d iq-запросов, а также выполнено %(cmd)d команд. " % (gInfo)
	memUsage = getUsedMemorySize()
	if memUsage: 
		message += u"Используется %0.2f МБ памяти. " % (memUsage)
	user, system = os.times()[:2]
	message += u"Потрачено %.2f сек. процессора, %.2f сек. системного времени и в итоге %.2f сек. общесистемного времени. " % (user, system, user + system)
	message += u"Было запущено %(tmr)d таймеров, %(thr)d потоков, %(err)d из них с ошибками, " % (gInfo)
	message += u"в данный момент активно %d потоков" % (threading.activeCount())
	sendMsg(msgType, conference, nick, message)

registerCommand(showBotUptime, u"ботап", 10, 
				u"Показывает статистику работы бота", 
				None, 
				(u"ботап", ), 
				ANY | NONPARAM)
