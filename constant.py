import sys
import traceback
import socket
import logging
import json
import os
from datetime import datetime
import logging.config
import configparser

from chatbot.NLU.nlu_rule import NLU
from chatbot.NLG.nlg import NLG

class ConstantCenter():

    logger_config = json.load(open('./config/logger.json'), encoding='utf-8')
    app_env = configparser.ConfigParser()
    app_env.read('./config/app.env')
    nlu = NLU()
    nlg = NLG()
    if not os.path.exists(app_env['app']['SAVE_PATH']):
        os.makedirs(app_env['app']['SAVE_PATH'])
    if not os.path.exists('./log'):
        os.makedirs('./log')
    logging.config.dictConfig(logger_config['logging_settings'])
    host_addr = socket.gethostname()
    info_logger = logging.getLogger("info")
    error_logger = logging.getLogger("error")
    warning_logger = logging.getLogger("warning")


class AuthException(BaseException):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def get_code(self):
        return self.code

    def get_message(self):
        return self.message

class AppException(BaseException):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        
    def get_code(self):
        return self.code

    def get_message(self):
        return self.message

class DatabaseException(BaseException):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        
    def get_code(self):
        return self.code

    def get_message(self):
        return self.message


class RequestException(BaseException):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        
    def get_code(self):
        return self.code

    def get_message(self):
        return self.message