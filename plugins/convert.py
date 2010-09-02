# coding: utf-8;

# convert.py 
# Based on convert.py from Isida-bot
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

gValues = {u'AUD': u'Австралийский доллар', 
			u'ATS': u'Австрийский шиллинг', 
			u'GBP': u'Английский фунт стерлингов', 
			u'BYR': u'Белорусский рубль', 
			u'BEF': u'Бельгийский франк', 
			u'BRL': u'Бразильский реал', 
			u'HUF': u'Венгерский форинт', 
			u'NLG': u'Голландский гульден', 
			u'GRD': u'Греческая драхма', 
			u'DKK': u'Датская крона', 
			u'USD': u'Доллар США', 
			u'EUR': u'ЕВРО', 
			u'EGP': u'Египетский фунт', 
			u'INR': u'Индийская pупия', 
			u'IEP': u'Ирландский фунт', 
			u'ISK': u'Исландская крона', 
			u'ESP': u'Испанская песета', 
			u'ITL': u'Итальянская лира', 
			u'KZT': u'Казахский тенге', 
			u'CAD': u'Канадский доллар', 
			u'KGS': u'Киргизский сом', 
			u'CNY': u'Китайский юань', 
			u'KWD': u'Кувейтский динар', 
			u'LVL': u'Латвийский лат', 
			u'LTL': u'Литовский лит', 
			u'DEM': u'Немецкая марка', 
			u'NOK': u'Норвежская крона', 
			u'PLN': u'Польский злотый', 
			u'PTE': u'Португальский эскудо', 
			u'RUR': u'Российский рубль', 
			u'SDR': u'СДР', 
			u'XDR': u'СДР(спец. права заимствования)', 
			u'SGD': u'Сингапурский доллар', 
			u'TRL': u'Турецкая лира', 
			u'TRY': u'Турецкая лира', 
			u'UZS': u'Узбекский сум', 
			u'UAH': u'Украинская гривна', 
			u'FIM': u'Финляндская марка', 
			u'FRF': u'Французский франк', 
			u'CZK': u'Чешская крона', 
			u'SEK': u'Шведская крона', 
			u'CHF': u'Швейцарский франк', 
			u'EEK': u'Эстонская крона', 
			u'YUN': u'Югославский динар', 
			u'ZAR': u'Южноафриканский рэнд', 
			u'KRW': u'Южнокорейский вон', 
			u'JPY': u'Японская иена'
};

gConvPattern = re.compile('<TD><B>(.*?)</B>(.*?)<TD><B>(.*?)</B>(.*?)<TD><B>(.*?)</B></TD>', re.DOTALL);
gConvUrl = 'http://conv.rbc.ru/convert.shtml?mode=calc&source=cb.0&tid_from=%s&commission=1&tid_to=%s&summa=%s&day=%s&month=%s&year=%s';

def convertValues(msgType, conference, nick, param):
	if(param == u'валюты'):
		values = ['%s - %s' % (x, gValues[x]) for x in gValues];
		values.sort();
		sendMsg(msgType, conference, nick, '\n'.join(values));
	else:
		if(len(param.split()) == 3):
			param = param.upper().split();
			try:
				count = float(param[2]);
			except(ValueError):
				sendMsg(msgType, conference, nick, u'читай помощь по команде');
				return;
			frm = param[0];
			to = param[1];
			print (frm in gValues and to in gValues);
			if(frm in gValues):
				date = tuple(time.localtime())[:3];
				url = gConvUrl % (frm, to, count, date[2], date[1], date[0]);
				text = unicode(urllib.urlopen(url.replace('RUR', 'BASE')).read(), 'cp1251');
				items = gConvPattern.search(text);
				if(items):
					text = u'%s %s = %s %s\n1 %s = %s %s' % (count, frm, items.group(5), to, frm, items.group(3), to);
					text = text.replace('BASE', 'RUR');
					sendMsg(msgType, conference, nick, decode(text));
				else:
					sendMsg(msgType, conference, nick, u'не получается');
			else:
				sendMsg(msgType, conference, nick, u'читай помощь по команде');

registerCommand(convertValues, u'перевести', 10, u'Перевод валют. "валюты" в качестве параметра - список валют для перевода', u'перевести <из> <в> <кол-во>', (u'перевести RUR USD 100.5', u'перевести валюты'), ANY | PARAM);
