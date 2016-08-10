# -*- coding: utf-8 -*-


import time
import datetime
from os import walk
from os import path
import os
import shlex
import six
import sys
import uuid
import re
from subprocess import Popen,PIPE
from . import exceptions



def convert_timestamp(timestamp, formatstr='%Y-%m-%d %H:%M:%S'):
    timearray = time.localtime(timestamp)
    return time.strftime(formatstr, timearray)

def get_files(base_path, sub_path='', ext='', prefix='') :
    '''读取目录下所有的文件,返回文件的绝对路径和相对路径
        base_path 父目录
        sub_path 子目录
        ext 排除指定后缀的文件
        prefix 返回的相对路径前面是否要加前缀

    return ('/tmp/a/f1.txt','a/f1.txt')
    '''
    file_list = []
    base_path = base_path if base_path.endswith('/') else base_path + '/'
    for root, dirs, files in walk(path.join(base_path, sub_path)):
        relativeroot = root.replace(base_path, '', 1)
        if prefix:
            relativeroot = path.join(prefix, relativeroot)
            
        _file_list = [(path.join(root, file_name),path.join(relativeroot, file_name))
                         for file_name in files 
                         if file_name.endswith(ext)]
        file_list.extend(_file_list)
    return iter(sorted(file_list))


def get_day(days=1, formatstr='%Y%m%d'):
    '''返回多少天之前的时间字符串
    默认返回昨天的时间字符串：20160508
    '''
    if re.match(r'^\d$',str(days)):
        day = datetime.datetime.now() - datetime.timedelta(days=days)
        return day.strftime(formatstr)
    elif re.match(r'^20\d{6,6}$',str(days)):
        return str(days)
    else:
        raise exceptions.FormatException(u'格式不正确')

def get_hostname():
    cmd = 'hostname -f'
    p = Popen(shlex.split(cmd), stdout=PIPE)
    return p.stdout.readline().strip('\n')

def delete_files(curdir):
    for root, dirs, files in walk(curdir):
        for file_name in files:
            if file_name.endswith('.log'):
                _file = path.join(root, file_name)
                os.remove(_file)

def get_uuid():
    return uuid.uuid1().hex

def safe_decode(text, incoming=None, errors='strict'):
    if not isinstance(text, (six.string_types, six.binary_type)):
        raise TypeError("%s can't be decoded" % type(text))

    if isinstance(text, six.text_type):
        return text

    if not incoming:
        incoming = (sys.stdin.encoding or
                    sys.getdefaultencoding())

    try:
        return text.decode(incoming, errors)
    except UnicodeDecodeError:
        return text.encode('utf-8', errors)