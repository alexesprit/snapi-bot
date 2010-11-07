# coding: utf-8

# hddtemp.py
# Initial Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showHDDTempOutput(msgType, conference, nick, param):
	pipe = os.popen("ls /dev/ | grep \"sd\"")
	output = pipe.read()
	pipe.close()
	
	disks = re.findall(r"(sd.)[^\d]", output)
	message = []
	if disks:
		for disk in disks:
			pipe = os.popen("hddtemp /dev/%s" % (disk))
			output = pipe.read()
			pipe.close()	

			message.append(output)
		sendMsg(msgType, conference, nick, "\n".join(message))
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

registerCommand(showHDDTempOutput, u"hddtemp", 100, 
				u"Показывает вывод программы hddtemp для всех дисков", 
				None, 
				(u"hddtemp", ), 
				ANY | NONPARAM)