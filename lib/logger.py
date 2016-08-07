# coding=utf-8
import logging
import logging.config
from cloghandler import ConcurrentRotatingFileHandler

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': "[%(levelname)1.1s%(asctime)s.%(msecs)03d|%(process)d|%(module)s.%(funcName)s:%(lineno)d] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'fileInfo': {
            'level': 'DEBUG',
            'class': 'cloghandler.ConcurrentRotatingFileHandler',
            # 当达到10MB时分割日志
            'maxBytes': 1024 * 1024 * 10,
            # 最多保留50份文件
            'backupCount': 50,
            # If delay is true,
            # then file opening is deferred until the first call to emit().
            'delay': True,
            'filename': '/data/logs/mysite.log',
            'formatter': 'verbose'
        },
        'fileError': {
            'level': 'DEBUG',
            'class': 'cloghandler.ConcurrentRotatingFileHandler',
            # 当达到10MB时分割日志
            'maxBytes': 1024 * 1024 * 10,
            # If delay is true,
            # then file opening is deferred until the first call to emit().
            'delay': True,
            'filename': '/data/logs/mysite.error.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'info': {
            'handlers': ['fileInfo'],
            'level': 'INFO',
        },
        'error': {
            'handlers': ['fileError'],
            'level': 'INFO',
        },
    }
})

loggerInfo = logging.getLogger('info')
loggerError = logging.getLogger('error')
info, error = loggerInfo.info, loggerError.error

if __name__ == '__main__':
    logger = logging.getLogger('error')
    logger.info('error info')
    logger = logging.getLogger('info')
    logger.info('log info')
