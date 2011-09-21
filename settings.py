import os

ROOT = '/'
CACHE_PATH = os.path.join(os.getcwd(), 'imagecache')
ERROR_STYLE = 'html'

IMAGES_DB = os.path.join(os.getcwd(), 'images.sqlite')

CACHES = {
    'default': {
        'BACKEND': 'cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 90000
    }
}
