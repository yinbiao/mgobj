# -*- coding: utf-8 -*-


import logging 


LOG = logging.getLogger(__name__)


class BaseException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class FormatException(BaseException):
    pass

