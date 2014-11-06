# coding: utf-8

# Initial Copyright (c) esprit

# NTP code is written by Firat Atagun
# http://www.firatatagun.com/python-ntp-client/

import socket
import struct

import pytz

from pytz import timezone
from datetime import datetime

WEEKDAYS = (u"понедельник", u"вторник", u"среда", u"четверг", u"пятница", u"суббота", u"воскресенье")
NTP_SERVER = "pool.ntp.org"
NTP_PACKET = "\x1b" + 47 * "\0"

def getUtcTime():
	try:
		server = (NTP_SERVER, 123)
		client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		client.sendto(NTP_PACKET, server)
		data = client.recvfrom(1024)[0]
		if data:
			seconds = struct.unpack('!12I', data)[10]
			if seconds:
				return seconds - 2208988800L
	except socket.error:
		pass
	return 0

def showMoscowTime(msgType, conference, nick, param):
	current_time = getUtcTime()
	if current_time:
		from_ntp = True
	else:
		from_ntp = False
		current_time = time.time()

	moscow_tz = timezone('Europe/Moscow')
	utc_dt = pytz.utc.localize(datetime.utcfromtimestamp(current_time))
	moscow_dt = utc_dt.astimezone(moscow_tz)
	time_str = moscow_dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')

	message = u"Московское время: {0}".format(time_str)
	sendMsg(msgType, conference, nick, message)

registerCommand(showMoscowTime, u"время", 10,
				u"Показывает точное московское время",
				None,
				None,
				CMD_ANY | CMD_NONPARAM)
