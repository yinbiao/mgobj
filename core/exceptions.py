# -*- coding: utf-8 -*-


import logging 


LOG = logging.getLogger(__name__)


class BaseException(Exception):
    def __init__(self, msg):
        pass

