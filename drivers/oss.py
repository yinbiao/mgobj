# -*- coding: utf-8 -*-

"""
阿里云OSS操作
"""

import oss2
import os


class _Base(object):

    def __init__(self, keyid, keysecret, endpoint, connect_timeout):
        self.keyid = os.getenv('OSS_ACCESSID', keyid)
        self.keysecret = os.getenv('OSS_ACCESSKEYSECRET', keysecret)
        self.endpoint = os.getenv('OSS_ENDPOINT', endpoint)
        self.connect_timeout = connect_timeout

    def _auth(self):
        return oss2.Auth(self.keyid, self.keysecret)

    def _service(self, auth):
        return oss2.Service(auth, self.endpoint, '', self.connect_timeout)


class ActionDriver(_Base):

    def __init__(self, keyid, keysecret, endpoint, connect_timeout=3000):
        super(ActionDriver, self).__init__(keyid, 
                                           keysecret, 
                                           endpoint, 
                                           connect_timeout)
        self.auth = self._auth()
        self.service = self._service(self.auth)

    def list_bucket(self):
        return oss2.BucketIterator(self.service)

    def get_bucket(self, name):
        return oss2.Bucket(self.auth, self.endpoint, name, '', self.connect_timeout)

    def create_bucket(self, name):
        bucket = self.get_bucket(name)
        bucket.create_bucket()

    def delete_bucket(self, name):
        bucket = self.get_bucket(name)
        bucket.delete_bucket()

    def get_bucket_acl(self, name):
        bucket = self.get_bucket(name)
        return bucket.get_bucket_acl().acl

    def set_bucket_acl_private(self, name):
        bucket = self.get_bucket(name)
        bucket.put_bucket_acl(oss2.BUCKET_ACL_PRIVATE)

    def list_object(self, bucket, prefix=None):
        '''列举bucket下的文件
        '''
        if prefix is None:
            return enumerate(oss2.ObjectIterator(bucket))
        else:
            return enumerate(oss2.ObjectIterator(bucket, prefix=prefix))

    def put_object_from_str(self, bucket, objectname, content, **kwargs):
        '''在云上新建一个文件，内容直接输入
            bucket 桶对象
            objectname 新建的文件名称
            content 文件的内容
        '''
        bucket.pu_object(objectname, content)

    def put_object_from_file(self, bucket, objectname, localfile):
        '''从本地上传文件到云
            bucket 桶对象
            objectname 新建的文件名称
            localfile 本地文件路径
        '''
        bucket.put_object_from_file(objectname, localfile)

    def delete_object(self, bucket, objectname):
        bucket.delete_object(objectname)

    def delete_objects(self, bucket, objects):
        '''批量删除对象
            bucket [object] 桶对象
            objects [array] 文件
        '''
        bucket.batch_delete_objects(objects)

    def head_object(self, bucket, objectname):
        '''查看对象的自定义元数据
            bucket [object] 桶对象
            objectname [str] 对象名称

            返回object 
                result.content_length 
                result.last_modified)
                result.headers
        '''
        return bucket.head_object(objectname)

    def update_head_object(self, bucket, objectname, meta):
        '''修改自定义元数据
            bucket [object] 桶对象
            objectname [str] 对象名称
            meta [dict] 元数据 {'x-oss-meta-author': 'Bertrand Russell'}
        '''
        bucket.update_object_meta(objectname, meta)

    def get_object_to_file(self, bucket, objectname, localfile):
        '''普通下载文件
            bucket [object] 桶对象
            objectname [str] OSS文件名称
            localfile [str] 保存到本地的文件名称
        '''
        bucket.get_object_to_file(objectname, localfile)






