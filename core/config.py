# -*- coding=utf-8 -*-

import ConfigParser
import os


class Config(object):

    def __init__(self, name="config.conf"):
        #这个获取的绝对路径是用户所在的路径
        #self.name = "{0}/{1}".format(os.path.abspath('.'), name)
        if name.startswith("/"):
            self.name = name
        else:
            self.name = "{0}/{1}".format(os.path.split(
                os.path.realpath("{0}/..".format(__file__)))[0], 
                name)
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.name)

    def sections(self):
        return self.config.sections()

    def options(self, section):
        if section:
            return self.config.options(section)
        else:
            return ""

    def get(self, section, option):
        return self.config.get(section, option)



