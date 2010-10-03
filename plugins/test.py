# coding: utf-8

# test.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showTest(msgType, conference, nick, param):
	sendMsg(msgType, conference, nick, u"две полоски o_O")

registerCommand(showTest, u"тест", 10, 
				u"Тест на беременность", 
				None, 
				(u"тест", ), 
				ANY | NONPARAM)
