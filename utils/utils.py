# coding: utf-8

# utils.py

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from __future__ import with_statement

import os
import re
import threading

HTML_ESC_MAP = (
	("&gt;", u">"), 
	("&lt;", u"<"),
	("&apos;", u"'"),
	("&quot;", u"\""),
	("&nbsp;", u" "),
	("&mdash;", u"—"),
	("&middot;", u"·")
)

XML_ESC_MAP = (
	("&gt;", ">"), 
	("&lt;", "<"),
	("&apos;", "'"),
	("&quot;", "\""),
)

smph = threading.BoundedSemaphore(1)

def unescapeXML(xml):
	for esc, char in XML_ESC_MAP:
		xml = xml.replace(esc, char)
	xml = xml.replace("&amp;", "&")
	return xml

def escapeXML(xml):
	xml = xml.replace("&", "&amp;")
	xml = xml.replace("\x0C", "")
	xml = xml.replace("\x1B", "")
	for esc, char in XML_ESC_MAP:
		xml = xml.replace(char, esc)
	return xml

def getEntityChar(char):
	return unichr(int(char.group(1)))

def unescapeHTML(html):
	for esc, char in HTML_ESC_MAP:
		html = html.replace(esc, char)
	html = html.replace("&amp;", "&")
	return re.sub("&#(\d+);", getEntityChar, html)

def ustr(text):
	if isinstance(text, unicode):
		return text
	try:
		text = text.__str__()
	except AttributeError:
		text = str(text)
	if not isinstance(text, unicode):
		return unicode(text, "utf-8")
	return text

def readFile(path, default=None, encoding=None):
	if isinstance(path, unicode):
		path = path.encode("utf-8")
	if os.path.exists(path):
		f = file(path)
		data = f.read()
		f.close()
		if encoding:
			data = data.decode(encoding)
		return data
	else:
		dirname = os.path.dirname(path)
		if not os.path.exists(dirname):
			os.makedirs(dirname)
		writeFile(path, default)
		return default

def writeFile(path, data, mode="w"):
	with smph:
		if isinstance(path, unicode):
			path = path.encode("utf-8")
		f = file(path, mode)
		f.write(data)
		f.close()
