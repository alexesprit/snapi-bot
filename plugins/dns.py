# coding: utf-8

# dns.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>

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

registerCommand(showDNSResponse, u"днс", 10, 
				u"Показывает ответ от DNS для определённого хоста или IP адреса", 
				u"<хост|IP>", 
				(u"server.tld", u"127.0.0.1"), 
				CMD_ANY | CMD_PARAM)
