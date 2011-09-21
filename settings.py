import os

ROOT = '/var/www/site/'
CACHE_PATH = '/var/www/cache/'
CACHE_URL = '/cache/'
ICONS_URL = '/icon/'
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'template')

ERROR_STYLE = 'html'

IMAGES_DB = '/var/www/sqlitedb/images.sqlite'

CACHES = {
    'default': {
        'BACKEND': 'cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 90000
    }
}
