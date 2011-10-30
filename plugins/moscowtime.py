# coding: utf-8

# Firat Atagun
# http://www.firatatagun.com/python-ntp-client/

import socket
import struct

WEEKDAYS = (u"понедельник", u"вторник", u"среда", u"четверг", u"пятница", u"суббота", u"воскресенье")

def showMoscowTime(msgType, conference, nick, param):
	server = ("pool.ntp.org", 123)
	reqdata = "\x1b" + 47 * "\0"
	fromntp = True

	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	client.sendto(reqdata, server)

	data = client.recvfrom(1024)[0]
	if data:
		seconds = struct.unpack('!12I', data)[10]
		if seconds == 0:
			seconds = int(time.time())
		currtime = time.gmtime(seconds - 2208988800L + 4 * 3600)
	else:
		fromntp = False
		currtime = time.localtime()
	timestr = time.strftime("%H:%M:%S, %d.%m.%y", currtime)
	if fromntp:
		message = u"Московское время: %s, %s" % (timestr, WEEKDAYS[currtime[6]])
	else:
		message = u"Локальное время: %s, %s" % (timestr, WEEKDAYS[currtime[6]])
	sendMsg(msgType, conference, nick, message)

registerCommand(showMoscowTime, u"время", 10,
				u"Показывает точное московское время",
				None,
				None,
				CMD_ANY | CMD_NONPARAM)
