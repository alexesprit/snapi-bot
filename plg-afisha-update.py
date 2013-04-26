# coding: utf-8 

import re

from module import io
from module import netutil

TZONES_CACHE_FILE = 'afisha-cache.txt'
AFISHA_CITIES_PATH = 'afisha-cities.txt'
TIME_OFFSETS_PATH = 'afisha-tzones.txt'

AFISHA_RU_URL = "http://www.afisha.ru/"

def getCityTimeZone(city):
	def parseTZone(url):
		data = netutil.getURLResponseData(url, encoding='utf-8')
		if data:
			gmt = re.search(r'<a href="/wiki/.+?" title="UTC\+\d+">UTC\+(\d+)</a>', data)
			if gmt:
				tzone = gmt.group(1)
				return tzone
		return None
	query = netutil.quote(city)
	url = "http://ru.wikipedia.org/wiki/%s" % (query)
	tzone = parseTZone(url)
	if tzone:
		return tzone
	query = netutil.quote(u'%s (город)' % city)
	url = u"http://ru.wikipedia.org/wiki/%s" % (query)
	tzone = parseTZone(url)
	if tzone:
		return tzone
	return "???"

def getCitiesData():
	tzoneCache = io.load(TZONES_CACHE_FILE, {})
	afishaData = []
	data = netutil.getURLResponseData(AFISHA_RU_URL, encoding='utf-8')
	items = re.findall(r'<a href="http://www.afisha.ru/(.+?)/changecity/">(.+?)</a>', data)
	for item in items:
		city = item[1]
		code = item[0]	
		if city.lower() in tzoneCache:
			tzone = tzoneCache[city.lower()]
		else:
			tzone = getCityTimeZone(city)
			if tzone != "???":
				tzoneCache[city.lower()] = tzone
		afishaData.append((city, code, tzone))
		print "%s [%s] UTC+%s" % (city, code, tzone)
	io.dump(TZONES_CACHE_FILE, tzoneCache)
	return afishaData

def updateAfishaCities():
	citiesOut = open("afisha-cities.txt", 'wb')
	citiesOut.write("{\n")
	tzonesOut = open('afisha-tzones.txt', 'wb')
	tzonesOut.write('{\n')

	for data in getCitiesData():
		city, code, tzone = data
		hastZone = True
		if tzone == '???':
			hastZone = False
			tzone = "0"
		if ' ' in city:
			citiesOut.write('#')
			tzonesOut.write('#')
		citiesOut.write('u"%s": "%s", ' % (city.lower().encode('utf-8'), code.encode('utf-8')))
		tzonesOut.write('"%s": %s, ' % (code.encode('utf-8'), tzone))
		if not hastZone:
			tzonesOut.write('# not detected')

		citiesOut.write('\n')
		tzonesOut.write('\n')
		
	citiesOut.write('}\n')
	citiesOut.close()
	tzonesOut.write('}\n')
	tzonesOut.close()

updateAfishaCities()