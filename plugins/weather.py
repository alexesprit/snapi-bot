# coding: utf-8;

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

WCODES_FILE = 'weather.txt';
PRECIPITATION = {'4': u'дождь', 
				'5': u'ливень', 
				'6': u'снег',
				'7': u'снег',
				'8': u'буря',
				'9': u'нет данных',
				'10': u'без осадков'
};

def getWCodeByName(city):
	city = city.encode('utf-8');
	fileName = getFilePath(RESOURCE_DIR, WCODES_FILE)
	for line in open(fileName):
		if(line.startswith(city)):
			return(line.split('|')[1]);
	return(None);

def showWeather(msgType, conference, nick, param):
	city = param.capitalize();
	code = getWCodeByName(city);
	if(code):
		rawXml = urllib.urlopen('http://informer.gismeteo.ru/xml/%s.xml' % (code.strip())).read();
		node = xmpp.simplexml.XML2Node(rawXml);
		node = node.getTag('REPORT').getTag('TOWN');
		message = u'Погода в городе %s:\n' % (city);
		for forecast in node.getTags('FORECAST'):
			attrs = forecast.getAttrs();
			message += u'%(day)s.%(month)s, %(hour)s:00\n'% (attrs);
			
			temp = forecast.getTag('TEMPERATURE').getAttrs();
			message += u'Температура: %(min)s-%(max)s°C\n' % (temp);

			weather = forecast.getTag('PHENOMENA').getAttrs();
			message += u'Осадки: %s\n' % (PRECIPITATION[weather['precipitation']]);
			
			pressure = forecast.getTag('PRESSURE').getAttrs();
			message += u'Давление: %(min)s-%(max)s мм рт. ст.\n' % (pressure);
			
			hudmity = forecast.getTag('RELWET').getAttrs();
			message += u'Влажность: %(min)s-%(max)s%%\n' % (hudmity);
			
			wind = forecast.getTag('WIND').getAttrs();
			message += u'Ветер: %(min)s-%(max)s м/с\n\n' % (wind);
		if(PUBLIC == msgType):
			sendMsg(msgType, conference, nick, u'ушла в приват');
		sendMsg(PRIVATE, conference, nick, message);
	else:
		sendMsg(msgType, conference, nick, u'не могу :(');

registerCommand(showWeather, u'погода', 10, u'Показывает погоду', u'погода <город>', (u'погода Москва', ), ANY | PARAM);
