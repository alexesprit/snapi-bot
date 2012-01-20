# coding: utf-8

# timetable.py
# Initial Copyright (с) 2010 -Esprit-

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
	response = getURL(url, qparam)
	if response:
		rawhtml = response.read()
		rawhtml = unicode(rawhtml, "utf-8")
		table = []
		
		rawhtml = re.search("</thead>(.+?)<div class=\"b-yadirect\">", rawhtml, re.DOTALL).group(1)

		transports = re.findall(u"<div class=\"b-timetable__tripname\">(.+?)</div>", rawhtml, re.DOTALL)
		descs = re.findall(u"<div class=\"b-timetable__description\">(.+?)</div>", rawhtml, re.DOTALL)
		platforms = re.findall(u"<div class=\"b-timetable__platform\">(.+?)</div>", rawhtml, re.DOTALL)
		times = re.findall(u"<div class=\"b-timetable__time\">(.+?)</div>", rawhtml, re.DOTALL)
		places = re.findall(u"<td class=.+?column_type_price\">(.+?)</td>", rawhtml, re.DOTALL)
		
		count = len(transports)

		for i in xrange(count):
			if "gone" in places[i]:
				continue
				
			transport = decode(transports[i]).strip()
			desc = decode(descs[i]).strip()
			source = decode(platforms[2 * i + 0]).strip()
			target = decode(platforms[2 * i + 1]).strip()
			departure = decode(times[2 * i]).strip()
			arrival = decode(times[2 * i + 1]).strip()
			
			table.append([transport, desc, source, departure, target, arrival])
		return table
	else:
		return None

def showTrainTable(msgType, conference, nick, param):
	param = param.split(None, 1)
	if len(param) == 2:
		cities = param[1]
		if cities.count(">"):
			cityFrom, cityTo = cities.split(">")
			date = param[0]
			tableList = getTrainTable(cityFrom, cityTo, date)
			message = []
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
				u"<дата> <место_отправления > место прибытия>", 
				(u"12.09 Котлас > Ярославль", ), 
				CMD_ANY | CMD_PARAM)
