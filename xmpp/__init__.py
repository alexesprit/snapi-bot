# $Id: __init__.py,v 1.9 2005/03/07 09:34:51 snakeru Exp $

"""
	All features of xmpppy library contained within separate modules.
	At present there are modules:
		* auth - SASL stuff. You will need it to auth as a client or transport
		* debug - Jacob Lundquist's debugging module. Very handy if you like colored debug
		* dispatcher - decision-making logic. Handles all hooks. The first who takes control 
		  over fresh stanzas
		* protocol: jabber-objects (I.e. UserJID and different stanzas and sub-stanzas)
		* roster - simple roster for use in clients
		* simplexml - XML handling routines
		* transports - low level connection handling. TCP and TLS currently. HTTP support planned

	Most of the classes that is defined in all these modules is an ancestors of 
	class PlugIn so they share a single set of methods allowing you to compile 
	a featured XMPP client. For every instance of PlugIn class the 'owner' is the class
	in what the plug was plugged. While plugging in such instance usually sets some
	methods of owner to it's own ones for easy access. All session specific info stored
	either in instance of PlugIn or in owner's instance. This is considered unhandy
	and there are plans to port 'Session' class from xmppd.py project for storing all
	session-related info. Though if you are not accessing instances variables directly
	and use only methods for access all values you should not have any problems.
"""
