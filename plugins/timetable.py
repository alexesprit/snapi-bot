# coding: utf-8

# timetable.py
# Initial Copyright (с) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def getTrainTable(cityFrom, cityTo, dateForward):
	url = "http://rasp.yandex.ru/search"
	qparam = {
		"cityFrom": cityFrom.encode("utf-8"),
		"cityTo": cityTo.encode("utf-8"),
		"dateForward": dateForward.encode("utf-8")
	}
	data = netutil.getURLResponseData(url, qparam, encoding='utf-8')
	if data:
		transports = re.findall(u'<div class="b-timetable__tripname">(.+?)</div>', data)
		descriptions = re.findall(u'<div class="b-timetable__description">(.+?)</div>', data)
		platforms = re.findall(u'<div class="b-timetable__holder-name">(.+?)</div>', data)
		times = re.findall(u'<span class="b-timetable__time.+?">(.+?)</span>', data)
		places = re.findall(u'<td class="b-timetable__cell b-timetable__cell_type_tariff">(.+?)</td>', data)
		
		table = []
		count = len(transports)
		for i in xrange(count):
			if 'gone' in places[i]:
				continue
			transport = netutil.removeTags(transports[i])#.strip()
			description = netutil.removeTags(descriptions[i])#.strip()
			departurePlace = netutil.removeTags(platforms[2 * i + 0])#.strip()
			arrivalPlace = netutil.removeTags(platforms[2 * i + 1])#.strip()
			departureTime = netutil.removeTags(times[2 * i])#.strip()
			arrivalTime = netutil.removeTags(times[2 * i + 1])#.strip()
			
			table.append([transport, description, departurePlace, departureTime, arrivalPlace, arrivalTime])
		return table
	else:
		return None

def showTrainTable(msgType, conference, nick, param):
	DATE_RE_PATTERN = '[0-9]+\.[0-9]+'

	if re.search(DATE_RE_PATTERN, param):
		args = re.split(DATE_RE_PATTERN, param)
		date = args[0]
		cities = args[1]
	else:
		date = time.strftime('%d.%m', time.localtime())
		cities = param

	if cities.count(">"):
		cityFrom, cityTo = cities.split(">")
		tableList = getTrainTable(cityFrom, cityTo, date)
		message = [u'Расписание на %s:' % date]
		msgText = u"%d) %s\n%s\nОтправление: %s; %s\nПрибытие: %s; %s\n"
		if tableList:
			for i, table in enumerate(tableList):
				message.append(msgText % (i + 1, table[0], table[1], table[2], table[3], table[4], table[5]))
			if protocol.TYPE_PUBLIC == msgType:
				sendMsg(msgType, conference, nick, u"ушло")
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, "\n".join(message))
		else:
			sendMsg(msgType, conference, nick, u"Не найдено!")
	else:
		sendMsg(msgType, conference, nick, u"Читай помощь по команде")

registerCommand(showTrainTable, u"расписание", 10, 
				u"Показывает расписание поездов",
				u"[дата] <место_отправления > место прибытия>", 
				(u"Котлас > Ярославль", u"12.09 Котлас > Ярославль"), 
				CMD_ANY | CMD_PARAM)
