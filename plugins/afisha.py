# coding: utf8

# afisha.py
# module for getting cinema schedule from http://www.afisha.ru
# Copyright (C) 2008 Tikhonov Andrey aka Tishka17 
#
# This module is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

AFISHA_CITIES = {
	u"москва": "msk",
	u"петербург": "spb", 
	u"волгоград": "volgograd",
	u"воронеж": "voronezh", 
	u"екатеринбург": "ekaterinburg",
	u"иркутск": "irkutsk",
	u"казань": "kazan",
	u"калининград": "kaliningrad",
	u"краснодар": "krasnodar",
	u"липецк": "lipetsk",
	u"мурманск": "murmansk",
	u"новгород": "nnovgorod",
	u"новосибирск": "novosibirsk",
	u"омск": "omsk",
	u"пермь": "perm",
	u"петрозаводск": "petrozavidsk",
	u"ростов-на-дону": "rostov-na-donu",
	u"самара": "samara",
	u"сочи": "sochi",
	u"ставрополь": "stavropol",
	u"тула": "tula",
	u"уфа": "ufa",
	u"челябинск": "chelyabinsk",
	u"ярославль": "yaroslavl",
	u"киев": "kiev",
	u"харьков": "harkov",
	u"донецк": "donetsk"
}

TIME_OFFSET = {
	"msk": 4,
	"spb": 4,
	"volgograd": 4,
	"voronezh": 4,
	"ekaterinburg": 6,
	"irkutsk": 4,
	"kazan": 4,
	"kaliningrad": 3,
	"krasnodar": 4,
	"lipetsk": 4,
	"murmansk": 4,
	"nnovgorod": 4,
	"novosibirsk": 7,
	"perm": 6,
	"petrozavodsk": 4,
	"rostov-na-donu": 4,
	"samara": 4, 
	"sochi": 4,
	"stavropol": 4,
	"tula": 4,
	"ufa": 6,
	"chelyabinsk": 6,
	"yaroslavl": 4,
	"kiev": 2,
	"harkov": 2,
	"donetsk": 2
}

gAfishaCache = {}

def compareTimes(x, y):
	if (x[3] > y[3] and \
		(y[3] > 3 or (y[3] <= 3 and x[3] <= 3))) or	\
		(x[3] == y[3] and x[4] > y[4]) or \
		(x[3] <= 3 and y[3] > 3):
			return 1
	#if (y[3] > x[3] and (x[3] > 3 or \
	#	(x[3] <= 3 and y[3] <= 3))) or \
	#	(y[3] == x[3] and y[4] > x[4]) or \
	#	(y[3] <= 3 and x[3] > 3):
	#		return -1
	return -1

def compareSchedules(a, b):
	if isinstance(a, tuple):
		a = time.strptime(a[2], "%H:%M")
	elif isinstance(a, basestring):
		a = time.strptime(a, "%H:%M")
	if isinstance(b, tuple):
		b = time.strptime(b[2], "%H:%M")
	elif isinstance(b, basestring):
		b = time.strptime(b, "%H:%M")
	return compareTimes(a, b)

def getFullSchedule(city):
	now = time.localtime()
	if city in gAfishaCache:
		lastupdate = gAfishaCache[city]["update"]
		x = time.localtime(gAfishaCache[city]["update"])
		x1 = time.localtime(gAfishaCache[city]["update"] - 86400)
		if (now[2] == x[2] and now[1] == x[1] and now[0] == x[0] and \
			(x[3] > 3 and now[3] > 3 or x[3] <= 3 and now[3] <= 3)) or\
			(now[2] == x1[2] and now[1] == x1[1] and now[0] == x1[0] and now[3] <= 3 and x1[3] > 3):
				return gAfishaCache[city]["schedule"]
	schedule = []
	url = "http://www.afisha.ru/%s/schedule_cinema/" % (city)
	data = netutil.getURLResponseData(url, encoding='utf-8')
	if data:
		getcinema = re.compile(u"class=\"b-td-item\">(?:[^>]+)>([^<]+)</a")
		gettime = re.compile(u"<span (?:[^>]+)>(?:\s*)([^\r]+)(?:\s*)<")
		gettime2 = re.compile(u"<a (?:[^>]+)>(?:\s*)([^\r]+)(?:\s*)<")
		list1 = re.split(u"<h3 class=\"usetags\">([^>]+)>(?:\s*)([^<]+)(?:\s*)<", data, re.DOTALL)
		timetable = re.compile(u"table>")
		films = zip(list1[2::3],list1[3::3])
		for film in films:
			list2 = getcinema.split(timetable.split(film[1])[1], re.DOTALL)
			cinemas = zip(list2[1::2], list2[2::2])
			for cinema in cinemas:
				list3 = gettime.split(cinema[1],re.DOTALL)
				for time1 in list3[1::2]:
					if gettime2.match(time1):
						if gettime2.split(time1)[1].find(":") > -1:
							schedule.append((film[0], cinema[0], gettime2.split(time1)[1]))
					else:
						if time1.find(":") > -1:
							schedule.append((film[0], cinema[0], time1))
		schedule.sort(compareSchedules)
		gAfishaCache[city] = {}
		gAfishaCache[city]["update"] = time.time()
		gAfishaCache[city]["schedule"] = schedule
	return schedule

def getCityTime(city):
	now = time.gmtime(time.time() + (TIME_OFFSET[city]) * 3600)
	return now

def getCinemas(city):
	schedule = getFullSchedule(city)
	cinemas = list(set([i[1] for i in schedule]))	
	cinemas.sort()
	return cinemas

def getFilms(city):
	schedule = getFullSchedule(city)
	films = list(set([i[0] for i in schedule]))	
	films.sort()
	return films
	
def getCities():
	return sorted(AFISHA_CITIES.keys())

def getSchedule(city, now, cinema, film):
	ls = []
	schedule = getFullSchedule(city)
	n = 0
	for i in schedule:
		if (not cinema or cinema.lower() == i[1].lower()) and (not film or film.lower() == i[0].lower()) and (not now or compareSchedules(i[2], now) == 1):
				ls.append(i)
				n += 1
				if n > 9:
					break
	return ls

def showAfisha(msgType, conference, nick, param):
	hasDate = re.search(u"\d:\d", param)
	if hasDate:
		args = param.split(None, 2)
	else:
		args = param.split(None, 1)
	arglen = len(args)

	city = args[0].lower()
	if city not in AFISHA_CITIES:
		citieslist = u", ".join(city.capitalize() for city in getCities())
		sendMsg(msgType, conference, nick, 
			u"Укажите, пожалуйста, один из следующих городов: %s" % (citieslist))
		return
	cityCode = AFISHA_CITIES[city]
	city = city.capitalize()

	if arglen > 1:
		if hasDate:
			try:
				now = time.strptime(args[1], "%H:%M")
			except ValueError:
				now = getCityTime(cityCode)
		else:
			now = getCityTime(cityCode)
		cinema = args[arglen - 1].capitalize()
	else:
		now = getCityTime(cityCode)
		cinema = None
	timestr = time.strftime(u"%H:%M", now)

	if not cinema:
		schedule = getSchedule(cityCode, now, None, None)
		if schedule:
			filmslist = "\n".join([u"%s: %s (%s)" % (i[2], i[0], i[1]) for i in schedule])
			if protocol.TYPE_PUBLIC == msgType:
				sendMsg(msgType, conference, nick, u"В привате")
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, 
				u"После %s в городе %s пройдут фильмы:\n%s" % (timestr, city, filmslist))
		else:
			sendMsg(msgType, conference, nick, 
				u"После %s в городе %s фильмов не найдено" % (timestr, city))
	elif cinema.lower() in [i.lower() for i in getCinemas(cityCode)]:
		schedule = getSchedule(cityCode, now, cinema, None)
		if schedule:
			filmslist = "\n".join([u"%s: %s (%s)" % (i[2], i[0], i[1]) for i in schedule])
			if protocol.TYPE_PUBLIC == msgType:
				sendMsg(msgType, conference, nick, u"В привате")
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, 
				u"После %s в кинотеатре %s пройдут фильмы:\n%s" % (timestr, cinema, filmslist))
		else:
			sendMsg(msgType, conference, nick, 
				u"После %s в кинотеатре %s фильмов не будет" % (timestr, cinema))
	elif cinema.lower() in [i.lower() for i in getFilms(cityCode)]:
		schedule = getSchedule(cityCode, now, None, cinema)
		if schedule:
			cinemalist = u"\n".join([u"%s: %s" % (i[2], i[1]) for i in schedule])
			if protocol.TYPE_PUBLIC == msgType:
				sendMsg(msgType, conference, nick, u"В привате")
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, 
				u"После %s фильм %s пройдет в следующих кинотеатрах:\n%s" % (timestr, cinema, cinemalist))
		else:
			sendMsg(msgType, conference, nick, 
				u"После %s фильм %s не найден" % (timestr, cinema))
	else:
		cinemalist = u", ".join(getCinemas(cityCode))
		filmslist = u", ".join(getFilms(cityCode))
		sendMsg(msgType, conference, nick, 
			u"Укажите кинотеатр, расписание которого Вы хотите посмотреть:\n%s\nили один из фильмов:\n%s" % (cinemalist, filmslist))
	
registerCommand(showAfisha, u"афиша", 10, 
				u"Показывает расписание кинотеатров",
				u"<город> [время] [фильм|кинотеатр]", 
				(u"Уфа", u"Уфа 19:00", u"Уфа Семья", u"Уфа 08:00 Терминатор 4"), 
				CMD_ANY | CMD_PARAM)
