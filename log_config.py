from logging.config import dictConfig
import house

PATH = house.__path__._path[0]+ "/log/"

LOGGING_CONFIG = { 
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'simple': { 
         "format": "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d %(message)s ;;;"
 } ,
    },
    'handlers': { 
        'default': { 
            'level': 'INFO',
            'formatter': 'simple',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stde
        },
        "file_handler":{
            "class": "logging.handlers.RotatingFileHandler",
            "level":"ERROR",
            "formatter":"simple",
            "filename":fr"{PATH}main.log",
            "maxBytes": 1048576,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "debugger":{
            "class": "logging.handlers.RotatingFileHandler",
            "level":"DEBUG",
            "formatter":"simple",
            "filename":fr"{PATH}debugger.log",
             "maxBytes": 1048576,
             "backupCount": 20,
             "encoding": "utf8" 
             },
       "flask_handler":{
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG", 
            "formatter": "simple",
            "filename":  fr"{PATH}flask.log",
            "maxBytes": 1048576,
            "backupCount": 20,
             "encoding": "utf8"
        },
       "testing":{
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG", 
            "formatter": "simple",
            "filename":  fr"{PATH}test.log",
            "maxBytes": 1048576,"backupCount": 20,
             "encoding": "utf8" 
            }
        },
    'loggers': { 
        "werkzeug":{
            "level": "DEBUG",
            "handlers": ["default", "flask_handler"]
        },
        "":{
            "level":"DEBUG",
            "handlers": ["default", "file_handler", "debugger"]
        },
        "test":{
            "level":"DEBUG",
            "handlers": ["testing"]
        }
    } 
}


dictConfig(LOGGING_CONFIG) 


