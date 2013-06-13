# coding: utf-8

# servers.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Initial Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import socket

def getDNSResponse(query):
	try:
		if not re.sub(r"\d+\.\d+\.\d+\.\d+", "", query):
			hostname = socket.gethostbyaddr(query)[0]
			return hostname
		else:
			ipaddrlist = socket.gethostbyaddr(query)[2]
			return u", ".join(ipaddrlist)
	except (socket.error):
		return None

def showDNSResponse(msgType, conference, nick, param):
	response = getDNSResponse(param.encode("utf-8"))
	if response:
		sendMsg(msgType, conference, nick, response)
	else:
		sendMsg(msgType, conference, nick, u"Не могу")

def showGeoIPInfo(msgType, conference, nick, param):
	host = param or Config.HOST or Config.SERVER
	url = "http://www.and-rey.ru/geoip/ie.php"
	qparam = {"host": host.encode("utf-8")}
	data = netutil.getURLResponseData(url, qparam, encoding='windows-1251')
	if data:
		elements = re.findall("<td class=red>(.+?)</td><td class=blue>(.+?)</td>", data)
		elements = [u"%s %s" % (element[0], element[1]) for element in elements]
		message = u"Инфо о %s:\n%s" % (host, netutil.removeTags("\n".join(elements)))
		sendMsg(msgType, conference, nick, message)
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

def showServerInfo(msgType, conference, nick, param):
	server = param or Config.SERVER
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_STATS)
	iq.setTo(server)
	gClient.sendAndCallForResponse(iq, showServerInfo_, (msgType, conference, nick, server))

def showServerInfo_(stanza, msgType, conference, nick, server):
	if protocol.TYPE_RESULT == stanza.getType():
		iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_STATS)
		iq.setQueryPayload(stanza.getQueryChildren())
		iq.setTo(server)
		gClient.sendAndCallForResponse(iq, showServerStats_, (msgType, conference, nick, server))
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

def showServerStats_(stanza, msgType, conference, nick, server):
	if protocol.TYPE_RESULT == stanza.getType():
		elements = []
		for stat in stanza.getQueryChildren():
			attrs = stat.getAttrs()
			if len(attrs) == 3:
				elements.append(u"%(name)s: %(value)s %(units)s" % (attrs))
		if elements:
			message = u"Инфа о %s:\n%s" % (server, "\n".join(elements))
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

def showServerUptime(msgType, conference, nick, param):
	server = param or Config.SERVER
	iq = protocol.Iq(protocol.TYPE_GET, protocol.NS_LAST)
	iq.setTo(server)
	gClient.sendAndCallForResponse(iq, showServerUptime_, (msgType, conference, nick, server))
	
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

def showServerUptime_(stanza, msgType, conference, nick, server):
	if protocol.TYPE_RESULT == stanza.getType():
		child = stanza.getFirstChild()
		seconds = int(child.getAttr("seconds"))
		if seconds:
			sendMsg(msgType, conference, nick, u"Время работы %s: %s" % (server, getUptimeStr(seconds)))
		else:
			sendMsg(msgType, conference, nick, u"Нет информации")
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

registerCommand(showDNSResponse, u"днс", 10, 
				u"Показывает ответ от DNS для определённого хоста или IP адреса", 
				u"<хост|IP>", 
				(u"server.tld", u"127.0.0.1"), 
				CMD_ANY | CMD_PARAM)
registerCommand(showGeoIPInfo, u"геоип", 10,
				u"Показывает информацию о географическом месторасположении хоста",
				u"[сервер]",
				(None, u"server.tld"))
registerCommand(showServerInfo, u"инфа", 10,
				u"Возвращает статистику jabber-сервера",
				u"[сервер]",
				(None, u"server.tld"))
registerCommand(showServerUptime, u"аптайм", 10,
				u"Показывает аптайм jabber-сервера",
				u"[сервер]",
				(None, u"server.tld"))
registerCommand(showWhoIs, u"хтоэто", 10, 
				u"Показывает информацию о домене", 
				u"<домен>", 
				(u"server.tld", ), 
				CMD_ANY | CMD_PARAM)
