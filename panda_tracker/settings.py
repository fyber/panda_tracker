from datetime import timedelta

MONGO_CONNECT = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
        }
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            # 'formatter': 'verbose'
        },
    },

    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}

JWT_EXPIRATION_DELTA = timedelta(days=7)
JWT_AUTH_URL_RULE = None
