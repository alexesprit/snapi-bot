# coding: utf-8

# учётная запись и пароль
JID = "username@server.tld"
PASSWORD = "secret"

# ресурс и приоритет
RESOURCE = "Snapi-Snup"
PRIORITY = 0

# станд. ник для конференций
NICK = u"Snapi-Snup"

# сервер и порт для подключения
HOST = "server.tld"
PORT = 5222

# 0 - отключить SSL/TLS
# 1 - автоопределение (SSL, если порт 443, 5223, иначе TLS)
# 2 - форсировать (нестандартный порт)
SECURE = 0
USE_RESOLVER = False

# список владельцев бота и пароль
ADMINS = ["admin@server.tld"]
ADMIN_PASSWORD = "secret"

# перезагружаться при ошибках?
RESTART_IF_ERROR = True

# папка для логов конференций
LOGGER_DIR = ""
