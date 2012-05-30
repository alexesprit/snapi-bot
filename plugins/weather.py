# coding: utf-8

# weather.py
# Initial Copyright (с) -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

WCODES_FILE = "citycodes.txt"

PRECIPITATION = {
	"4": u"дождь",
	"5": u"ливень",
	"6": u"снег",
	"7": u"снег",
	"8": u"гроза",
	"9": u"нет данных",
	"10": u"без осадков"
}

WINDDIRECTION = {
	"0": u"С",
	"1": u"С-В",
	"2": u"В",
	"3": u"Ю-В",
	"4": u"Ю",
	"5": u"Ю-З",
	"6": u"З",
	"7": u"С-З"
}

CLOUDINESS = {
	"0": u"ясно",
	"1": u"малооблачно",
	"2": u"облачно",
	"3": u"пасмурно"
}

def getWCodeByName(city):
	city = city.encode("utf-8").lower()
	path = getFilePath(RESOURCE_DIR, WCODES_FILE)
	for line in open(path):
		if line.lower().startswith(city):
			return line.split("|")
	return None

def getAverageValue(attr):
	minValue = int(attr["min"])
	maxValue = int(attr["max"])
	return (minValue + maxValue) / 2

def showWeather(msgType, conference, nick, param):
	rawdata = getWCodeByName(param)
	if rawdata:
		city, code = rawdata
		url = "http://informer.gismeteo.ru/xml/%s.xml" % (code.strip())
		response = getURL(url)
		if response:
			rawxml = response.read()
			node = simplexml.XML2Node(rawxml)
			node = node.getTag("REPORT").getTag("TOWN")
			buf = []

			buf.append(u"Погода в городе %s:\n" % (city.decode("utf-8")))
			for forecast in node.getTags("FORECAST"):
				attrs = forecast.getAttrs()
				buf.append(u"[%(day)s.%(month)s.%(year)s, %(hour)s:00]\n" % (attrs))

				weather = forecast.getTag("PHENOMENA").getAttrs()
				precValue = weather["precipitation"]
				cloudiness = CLOUDINESS[weather["cloudiness"]]
				precipitation = PRECIPITATION[precValue]
				if precValue not in ["8", "9", "10"]:
					rpower = weather["rpower"]
					if "0" == rpower:
						buf.append(u"%s, возможен %s\n" % (cloudiness, precipitation))
					else:
						buf.append(u"%s, %s\n" % (cloudiness, precipitation))
				elif "8" == precValue:
					spower = weather["spower"]
					if "0" == spower:
						buf.append(u"%s, возможна %s\n" % (cloudiness, precipitation))
					else:
						buf.append(u"%s, %s\n" % (cloudiness, precipitation))
				else:
					buf.append(u"%s, %s\n" % (cloudiness, precipitation))

				temp = forecast.getTag("TEMPERATURE").getAttrs()
				buf.append(u"Температура: %d°C\n" % (getAverageValue(temp)))

				pressure = forecast.getTag("PRESSURE").getAttrs()
				buf.append(u"Давление: %d мм рт. ст.\n" % (getAverageValue(pressure)))

				hudmity = forecast.getTag("RELWET").getAttrs()
				buf.append(u"Влажность: %s%%\n" % (getAverageValue(hudmity)))

				wind = forecast.getTag("WIND").getAttrs()
				windValue = getAverageValue(wind)
				if windValue:
					buf.append(u"Ветер: %d м/с (%s)\n" % (windValue, WINDDIRECTION[wind["direction"]]))
				buf.append("\n")
			if protocol.TYPE_PUBLIC == msgType:
				sendMsg(msgType, conference, nick, u"Ушла")
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, "".join(buf))
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")
	else:
		sendMsg(msgType, conference, nick, u"Город не найден!")

registerCommand(showWeather, u"погода", 10,
				u"Показывает погоду",
				u"<город>",
				(u"Москва", ),
				CMD_ANY | CMD_PARAM)
