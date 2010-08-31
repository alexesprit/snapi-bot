# coding: utf-8;

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

def showBotUptime(type, conference, nick, parameters):
	uptime = int(time.time() - gInfo['start']);
	message = u'я работаю уже %s, ' % (time2str(uptime));
	message += u'получено %(msg)d сообщений, обработано %(prs)d презенсов и %(iq)d iq-запросов, а также выполнено %(cmd)d команд. ' % (gInfo);
	memUsage = getUsedMemory();
	if(memUsage): 
		message += u'мной съедено %0.2f МБ памяти, ' % (memUsage);
	(user, system) = os.times()[:2];
	message += u'потрачено %.2f сек. процессора, %.2f сек. системного времени и в итоге %.2f сек. общесистемного времени. ' % (user, system, user + system);
	message += u'я запустила %(tmr)d таймеров, породила %(thr)d потоков, %(err)d из них с ошибками, ' % (gInfo);
	message += u'в данный момент активно %d потоков' % (threading.activeCount());
	sendMsg(type, conference, nick, message);

registerCommand(showBotUptime, u'ботап', 10, u'Показывает статистику работы бота', None, (u'ботап', ), ANY | NONPARAM);
