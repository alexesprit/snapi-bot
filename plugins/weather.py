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
				'8': u'гроза',
				'9': u'нет данных',
				'10': u'без осадков'
};

WINDDIRECTION = {'0': u'С', 
				'1': u'С-В',
				'2': u'В',
				'3': u'Ю-В',
				'4': u'Ю',
				'5': u'Ю-З',
				'6': u'З',
				'7': u'С-З'
};

CLOUDINESS = {'0': u'ясно',
				'1': u'малооблачно',
				'2': u'облачно',
				'3': u'пасмурно'
};

def getWCodeByName(city):
	city = city.encode('utf-8');
	fileName = getFilePath(RESOURCE_DIR, WCODES_FILE)
	for line in open(fileName):
		if(line.startswith(city)):
			return(line.split('|'));
	return(None);
	
def getAverageValue(attr):
	minValue = int(attr['min']);
	maxValue = int(attr['max']);
	return((minValue + maxValue) / 2);

def showWeather(msgType, conference, nick, param):
	city = param.capitalize();
	rawData = getWCodeByName(city);
	if(rawData):
		city, code = rawData;
		rawXml = urllib.urlopen('http://informer.gismeteo.ru/xml/%s.xml' % (code.strip())).read();
		node = xmpp.simplexml.XML2Node(rawXml);
		node = node.getTag('REPORT').getTag('TOWN');
		message = u'Погода в городе %s:\n' % (city.decode('utf-8'));
		for forecast in node.getTags('FORECAST'):
			attrs = forecast.getAttrs();
			message += u'[%(day)s.%(month)s.%(year)s, %(hour)s:00]\n'% (attrs);

			weather = forecast.getTag('PHENOMENA').getAttrs();
			message += CLOUDINESS[weather['cloudiness']];
			precipitation = weather['precipitation'];
			if(precipitation not in ['8', '9', '10']):
				rpower = weather['rpower'];
				if('0' == rpower):
					message += u', возможен %s\n' % (PRECIPITATION[precipitation]);
				else:
					message += u', %s\n' % (PRECIPITATION[precipitation]);
			elif('8' == precipitation):
				spower = weather['spower'];
				if('0' == rpower):
					message += u', возможна %s\n' % (PRECIPITATION[precipitation]);
				else:
					message += u', %s\n' % (PRECIPITATION[precipitation]);
			else:
				message += u', %s\n' % (PRECIPITATION[precipitation]);

			temp = forecast.getTag('TEMPERATURE').getAttrs();
			message += u'Температура: %d°C\n' % (getAverageValue(temp));

			pressure = forecast.getTag('PRESSURE').getAttrs();
			message += u'Давление: %d мм рт. ст.\n' % (getAverageValue(pressure));
			
			hudmity = forecast.getTag('RELWET').getAttrs();
			message += u'Влажность: %s%%\n' % (getAverageValue(hudmity));
			
			wind = forecast.getTag('WIND').getAttrs();
			windValue = getAverageValue(wind);
			if(windValue):
				message += u'Ветер: %d м/с (%s)\n' % (windValue, WINDDIRECTION[wind['direction']]);
			message += '\n';
		if(PUBLIC == msgType):
			sendMsg(msgType, conference, nick, u'ушла в приват');
		sendMsg(PRIVATE, conference, nick, message);
	else:
		sendMsg(msgType, conference, nick, u'не могу :(');

registerCommand(showWeather, u'погода', 10, u'Показывает погоду', u'погода <город>', (u'погода Москва', ), ANY | PARAM);
