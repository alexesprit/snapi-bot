# coding: utf-8;

# учётная запись и пароль
gJid = 'username@server.tld';
gPassword = 'secret';

# сервер и порт для подключения 
gHost = 'server.tld';
gPort = 5222;

# xmpp.SSL_DISABLE - отключить SSL
# xmpp.SSL_AUTO - автоопределение (порт 443 или 5223)
# xmpp.SSL_FORCE - форсировать (нестандартный порт)
gSSLMode = xmpp.SSL_DISABLE;
gUseResolver = False;

# ресурс и приоритет
gResource = 'Snapi-Snup';
gPriority = 0;

# станд. ник для конференций
gBotNick = u'Snapi-Snup';

# список владельцев бота и пароль
gAdmins = ['admin@server.tld'];
gAdminPass = 'secret';

# перезагружаться при ошибках?
gRestart = True;

# Описание флагов лога:
# always - все типы флагов
# read - чтение файлов
# write - запись файлов
# info - различные инф. сообщения
# error - ошибки
# success - успешные результаты
# warning - предупреждения
gCoreDebug = ['info', 'error', 'success', 'warning'];
# always - все типы флагов
# auth - авторизация
# bind - назначение ресурса
# dispatcher - обработка станз
# proxy - подклчение через прокси
# roster - работа с ростером
# socket - передаваемые данные
gXMPPDebug = [];

# папка для логов конференций
gLogDir = '';