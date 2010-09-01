# coding: utf-8;

# учётная запись и пароль
gJid = 'username@server.tld';
gPassword = 'secret';

# сервер и порт для подключения 
gHost = 'server.tld';
gPort = 5222;

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
# socket - содержимое передаваемых данных
# dispatcher - информация о принятых станзах
gXmppDebug = [];

# папка для логов конференций
gLogDir = '';