# -*- coding: utf-8 -*-

from .config import Config
from importlib import import_module
import logging

LOG = logging.getLogger(__name__)

class _Config(object):

    def __init__(self):
        self.config = Config()

class _Log(_Config):

    def __init__(self):
        super(_Log, self).__init__()
        logfile = self.config.get('logging', 'logfile')
        debug = self.config.get('logging', 'debug')
        if not logfile.startswith("/"):
            logfile = "{0}/{1}".format(os.path.abspath("."), logfile)
        if debug.lower() == "true":
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(level=level,  
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=logfile,  
                        filemode='a')


class Base(_Log):

    def __init__(self, keyid=None, keysecret=None, endpoint=None):
        super(Base, self).__init__()
        self.driver = self.config.get('main', 'driver')
        self.drivermod = import_module("drivers.{0}".format(self.driver))
        
        self.AccessKeyId = self.config.get(self.driver, 'AccessKeyId') \
            if keyid  is None else keyid
        self.AccessKeySecret = self.config.get(self.driver, 'AccessKeySecret') \
            if keysecret is None else keysecret
        self.EndPoint = self.config.get(self.driver, 'EndPoint') \
            if endpoint is None else endpoint

        self.Action = self.drivermod.ActionDriver(
            self.AccessKeyId, self.AccessKeySecret, self.EndPoint)


class Init(Base):

    def __init__(self, keyid=None, keysecret=None, endpoint=None):
        super(Init, self).__init__(keyid, keysecret, endpoint)
        
    def list_bucket(self):
        return self.Action.list_bucket()

    def get_bucket(self, name):
        return self.Action.get_bucket(name)

    def create_bucket(self, name):
        self.Action.create_bucket(name)

    def delete_bucket(self, name):
        self.Action.delete_bucket(name)

    def get_bucket_acl(self, name):
        return self.Action.get_bucket_acl(name)

    def set_bucket_acl_private(self, name):
        self.Action.set_bucket_acl_private(name)

    def list_object(self, bucket, prefix=None):
        '''输出bucket下的文件对象
            bucket [object] 桶对象
        return enumerate对象 
        for i, object_info in result:
            print("{0} {1}".format(object_info.last_modified, object_info.key))
        '''
        return self.Action.list_object(bucket, prefix)

    def put_object_from_str(self, bucket, objectname, content, **kwargs):
        '''在云上新建一个文件，内容直接输入
            bucket 桶对象
            objectname 新建的文件名称
            content 文件的内容
        '''
        self.Action.put_object_from_str(bucket, objectname, content, **kwargs)

    def put_object_from_file(self, bucket, objectname, localfile):
        '''从本地上传文件到云
            bucket 桶对象
            objectname 新建的文件名称
            localfile 本地文件路径
        '''
        self.Action.put_object_from_file(bucket, objectname, localfile)

    def delete_object(self, bucket, objectname):
        self.Action.delete_object(bucket, objectname)

    def delete_objects(self, bucket, objects):
        '''批量删除对象
            bucket [object] 桶对象
            objects [array] 文件
        '''
        self.Action.delete_objects(bucket, objects)

    def head_object(self, bucket, objectname):
        '''查看对象的自定义元数据
            bucket [object] 桶对象
            objectname [str] 对象名称

            返回object 
                result.content_length 
                result.last_modified)
                result.headers
        '''
        return self.Action.head_object(bucket, objectname)

    def update_head_object(self, bucket, objectname, meta):
        '''修改自定义元数据
            bucket [object] 桶对象
            objectname [str] 对象名称
            meta [dict] 元数据 {'x-oss-meta-author': 'Bertrand Russell'}
        '''
        self.Action.update_head_object(bucket, objectname, meta)

    def get_object_to_file(self, bucket, objectname, localfile):
        '''普通下载文件
            bucket [object] 桶对象
            objectname [str] 云上文件名称
            localfile [str] 保存到本地的文件名称
        '''
        self.Action.get_object_to_file(bucket, objectname, localfile)
