from logging.config import dictConfig
import torrent

PATH = torrent.__path__[0] + '/log/'


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d %(message)s\t"
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'simple',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stde
        },
        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "WARNING",
            "formatter": "simple",
            "filename": fr"{PATH}main.log",
            "maxBytes": 1048576,
            "backupCount": 20,
            "encoding": "utf8"
        }
    },
    'loggers': {
        "": {
            "level": "DEBUG",
            "handlers": ["default", "file_handler"]
        }
    }
}


dictConfig(LOGGING_CONFIG)
