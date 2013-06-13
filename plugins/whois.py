# coding: utf-8

# whois.py
# Initial Copyright (с) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showWhoIs(msgType, conference, nick, param):
	url = "http://1whois.ru/index.php"
	qparam = {"url": param.encode("idna")}
	data = netutil.getURLResponseData(url, qparam, encoding='windows-1251')
	if data:
		whoisRecord = re.search("<blockquote>(.+?)</blockquote>", data, re.DOTALL)
		recordData = whoisRecord.group(1)
		if u'Нет данных' in recordData:
			sendMsg(msgType, conference, nick, u"Не найдено!")
		else:
			records = re.findall(r'(.+?)\:([\w\s\-\.]+|\w+)\n', netutil.removeTags(whoisRecord.group(1)))
			buf = []
			for record in records:
				fieldName = record[0].strip()
				# text below is unused
				if fieldName == 'NOTICE':
					break
				fieldValue = record[1].strip()
				if fieldName and fieldValue:
					# fix for domain list output (e.g. github.com query)
					fieldValue = fieldValue.replace('\n      ', '')
					buf.append("%s: %s\n" % (fieldName, fieldValue))
			sendMsg(msgType, conference, nick, "".join(buf))
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showWhoIs, u"хтоэто", 10, 
				u"Показывает информацию о домене", 
				u"<адрес>", 
				(u"server.tld", ), 
				CMD_ANY | CMD_PARAM)
