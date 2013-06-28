# coding: utf-8 

import re

from module import io
from module import netutil

AFISHA_CITIES_PATH = 'afisha-cities.txt'
TIME_OFFSETS_PATH = 'afisha-tzones.txt'

AFISHA_RU_URL = "http://www.afisha.ru/"

gWorldTimeZonesRuData = {}
gKursrubRuData = {}

def getTimeZoneFromKursrubRu(city):
	global gKursrubRuData
	if not gKursrubRuData:
		data = netutil.getURLResponseData('http://kursrub.ru/cities-list.txt', encoding='utf-8')
		for item in data.splitlines():
			args = item.split(',')
			cityname = args[0]
			cityzone = args[10][1:] # args[10] = '+4', need 4
			gKursrubRuData[cityname] = cityzone
	return gKursrubRuData.get(city)

def getTimeZoneFromWorldTimeZonesRu(city):
	global gWorldTimeZonesRuData
	if not gWorldTimeZonesRuData:
		data = netutil.getURLResponseData('http://world-time-zones.ru/goroda.htm', encoding='windows-1251')
		items = re.findall(u'Часовой пояс г. (.+?)</td>.+?\(UTC\+(\d+)', data, re.DOTALL)
		for item in items:
			cityname = item[0]
			cityzone = item[1]
			gWorldTimeZonesRuData[cityname] = cityzone
	return gWorldTimeZonesRuData.get(city)

def getTimeZoneFromWikipedia(city):
	def parseTZone(url):
		data = netutil.getURLResponseData(url, encoding='utf-8')
		if data:
			gmt = re.search(r'<a href="/wiki/UTC.+?" title=".+?" class="mw-redirect">UTC\+(\d+)</a>', data)
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
	return None

def getCityTimeZone(city):
	getters = (
		getTimeZoneFromWorldTimeZonesRu,
		getTimeZoneFromKursrubRu,
		getTimeZoneFromWikipedia, 		
	)
	for getter in getters:
		tzone = getter(city)
		if tzone:
			return tzone
	return "???"

def getCitiesData():
	afishaData = []
	data = netutil.getURLResponseData(AFISHA_RU_URL, encoding='utf-8')
	items = re.findall(r'<a href="http://www.afisha.ru/(.+?)/changecity/">(.+?)</a>', data)
	for item in items:
		city = item[1]
		code = item[0]	
		tzone = getCityTimeZone(city)
		afishaData.append((city, code, tzone))
		print "%s [%s] UTC+%s" % (city, code, tzone)
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
