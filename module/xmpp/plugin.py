# plugin.py

# Copyright (C) 2003-2005 Alexey "Snake" Nezhdanov

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2,  or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

class PlugIn:
	""" Common xmpppy plugins infrastructure: plugging in/out, debugging.
	"""
	def __init__(self):
		self._exportedMethods = []
		self.debugFlag = self.__class__.__name__.lower()

	def plugIn(self, owner):
		""" Attach to main instance and register ourself and all our staff in it.
		"""
		self._owner = owner
		if self.debugFlag not in owner.debugFlags:
			owner.debugFlags.append(self.debugFlag)
		className = self.__class__.__name__
		if not hasattr(owner, className):
			self.printf("Plugging %s into %s" % (self, self._owner), "start")
			self._oldMethods = []
			for method in self._exportedMethods:
				methodName = method.__name__
				if hasattr(owner, methodName):
					self._oldMethods.append(getattr(owner, methodName))
				setattr(owner, methodName, method)
			setattr(owner, className, self)
			if hasattr(self, "plugin"):
				return self.plugin()
		else:
			self.printf("Another %s is already plugged" % (self), "error")
 
	def plugOut(self):
		""" Unregister all our staff from main instance and detach from it.
		"""
		self.printf("Plugging %s out of %s" % (self, self._owner), "stop")
		if hasattr(self, "plugout"):
			self.plugout()
		self._owner.debugFlags.remove(self.debugFlag)
		for method in self._exportedMethods:
			delattr(self._owner, method.__name__)
		for method in self._oldMethods:
			setattr(self._owner, method.__name__, method)
		delattr(self._owner, self.__class__.__name__)

	def printf(self, text, severity="info"):
		""" Feed a provided debug line to main instance's debug 
			facility along with our ID string. 
		"""
		self._owner.printf(text, self.debugFlag, severity)
