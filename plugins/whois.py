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
	qparam = {"url": param.encode("utf-8")}
	data = netutil.getURLResponseData(url, qparam, encoding='windows-1251')
	if data:
		serverInfo = re.search(r'<noindex><a target=_blank(.+?)<span id="srvrinfo">', data, re.DOTALL)
		if serverInfo:
			def getFields(rawdata):
				buf = []
				records = re.findall(r'(.+?)\:(.+?)\n', rawdata)
				for record in records:
					fieldName = record[0]
					fieldValue = record[1].strip()
					if fieldValue:
						buf.append("%s: %s\n" % (fieldName, fieldValue))
				return buf
			whoisRecord = re.search("<br />Domain.+?</blockquote>", data, re.DOTALL)
			buf = []
			buf.extend(getFields(netutil.removeTags(serverInfo.group(1))))
			buf.append('\n')
			buf.extend(getFields(netutil.removeTags(whoisRecord.group(0))))
		
			sendMsg(msgType, conference, nick, "".join(buf))
		else:
			sendMsg(msgType, conference, nick, u"Не найдено!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(showWhoIs, u"хтоэто", 10, 
				u"Показывает информацию о домене", 
				u"<адрес>", 
				(u"server.tld", ), 
				CMD_ANY | CMD_PARAM)
