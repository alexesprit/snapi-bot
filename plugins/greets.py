# coding: utf-8;

# greets.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

GREET_FILENAME = 'config/%s/greets.txt';

gGreets = {};

def setGreet(type, conference, nick, param):
	rawGreet = param.split('=', 1);
	if(len(rawGreet) == 2):
		userNick = rawGreet[0].strip();
		greet = rawGreet[1].strip();
		if(userNick.count('@')):
			trueJid = userNick;
		elif(userNick in getNicks(conference)):
			trueJid = getTrueJid(conference, userNick);
		else:
			sendMsg(type, conference, nick, u'а это кто?');
			return;
		if(not greet):
			if(trueJid in gGreets[conference]):
				del(gGreets[conference][trueJid]);
		else:
			gGreets[conference][trueJid] = greet;
		writeFile(GREET_FILENAME % (conference), str(gGreets[conference]));
		sendMsg(type, conference, nick, u'запомнила');

registerCommand(setGreet, u'приветствие', 30, u'Добавляет приветствие для определённого ника/жида', u'приветствие <ник/жид> = [текст]', (u'приветствие Nick = something', ), CHAT | PARAM);

def sendGreeting(conference, nick, trueJid, aff, role):
	if(trueJid in gGreets[conference]):
		sendMsg(PUBLIC, conference, nick, gGreets[conference][trueJid]);

registerJoinHandler(sendGreeting);

def loadGreetings(conference):
	fileName = GREET_FILENAME % (conference);
	createFile(fileName, '{}');
	gGreets[conference] = eval(readFile(fileName));

registerEvent(loadGreetings, ADDCONF);

def unloadGreetings(conference):
	del(gGreets[conference]);

registerEvent(unloadGreetings, DELCONF);