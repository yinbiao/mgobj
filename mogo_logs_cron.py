# -*- coding: utf-8 -*-


from __future__ import print_function
from core import base
from core import utils
import logging
import argparse
import sys
import os
import gzip

LOG = logging.getLogger(__name__)



class UploadLogs(object):

    def __init__(self):
        self.init = base.Init()
        self.yearsday = utils.get_day() #格式为：20160802
        self.hostname = utils.get_hostname() #获取主机名称
        self.nginxbucket = 'mogo-logs-nginx'
        self.tomcatbucket = 'mogo-logs-tomcat'
        self.nginxroot = self.init.config.get('main','nginxroot')
        self.tomcatroot = self.init.config.get('main','tomcatroot')
        self.status = True #检测整个脚本是否完全执行成功

    def _nginx_file_format(self, filepath, project, localtype=False, download=False):
        '''根据配置文件的文件路径返回本地要处理的文件格式和上传到OSS的文件格式
            filepath 配置文件指定的文件路径
            project 项目规范名称[partner renter等]
            localtype Boolean 返回本地格式或者OSS文件格式
            download Boolean 用于自定义下载时的本地文件路径
        '''
        if localtype:
            file = "{0}-{1}.gz".format(filepath, self.yearsday) #本地文件的格式
        elif download:
            _filename = os.path.split(filepath)[1]
            file = os.path.join(self.nginxroot, '{0}/{1}'.format(project,_filename))
        else:
            # _file = os.path.split(filepath)
            ossfilename = "{0}____{1}.gz".format(
                    self.yearsday, self.hostname) #OSS存储的文件名格式
            file = '{0}/{1}/{2}'.format(
                self.nginxbucket, 
                project,  
                ossfilename)
        return file

    def _tomcat_file_format(self, filepath, project, localtype=False, download=False):
        '''根据配置文件的文件路径返回本地要处理的文件格式和上传到OSS的文件格式
            filepath 配置文件指定的文件路径
            project 项目规范名称[partner renter等]
            localtype Boolean 返回本地格式或者OSS文件格式
            download Boolean 用于自定义下载时的本地文件路径
        '''
        filename = "{0}-{1}.gz".format('catalina.out', self.yearsday)
        if localtype:
            file = os.path.join(filepath, filename) #本地文件的格式
        elif download:
            _filename = os.path.split(filepath)[1]
            file = os.path.join(self.tomcatroot, '{0}/{1}'.format(project,_filename))
        else:
            hostname = filepath.split('/')[2] #从配置文件的定义中获取hostname
            ossfilename = "{0}____{1}.gz".format(
                self.yearsday, hostname) #OSS存储的文件名格式
            file = '{0}/{1}/{2}'.format(
                self.tomcatbucket, 
                project, 
                ossfilename)
        return file

    def get_nginx_files(self):
        '''获取需要上传的nginx文件
        返回格式：
        [('mogo-logs-nginx/partnerpc/20160803-hzb_web_1_3.gz', 
          '/data/logs/nginx/p.mogoroom.com.access.log-20160803.gz')]
        元组第一个元素为上传到OSS的对象名称
        元祖第二个元素为本地的文件路径
        '''
        nginx_project = self.init.config.options('nginx')
        files = []
        for _p in nginx_project:
            _file = self.init.config.get('nginx',_p)
            file = self._nginx_file_format(_file, _p, localtype=True)
            if os.path.isfile(file):
                yunfile = self._nginx_file_format(_file, _p)
                files.append((yunfile,file))
            else:
                LOG.warning(u'Nginx日志：{0} 没有找到'.format(file))
                self.status = False
        return files

    def get_tomcat_files(self):
        '''获取需要上传的tomcat文件
        返回格式：
        [('mogo-logs-tomcat/payapi/20160803-hzb_web_1_1.gz',
          '/logs/hzb_web_1_1/tomcat_payapi/catalina.out-20160803.gz')]
        元组第一个元素为上传到OSS的对象名称
        元祖第二个元素为本地的文件路径
        '''
        tomcat_project = self.init.config.options('tomcat')
        files = []
        for _p in tomcat_project:
            _dir = self.init.config.get('tomcat',_p).split('#')
            for _d in _dir:
                file = self._tomcat_file_format(_d, _p, localtype=True)
                if os.path.isfile(file):
                    yunfile = self._tomcat_file_format(_d, _p)
                    files.append((yunfile,file))
                else:
                    LOG.warning(u'Tomcat日志：{0} 没有找到'.format(file))
                    self.status = False
        return files

    def get_nginx_files_fromoss(self):
        '''根据配置文件的定义，返回需要从OSS上下载的文件列表
        返回格式：
        [('mogo-logs-nginx/partnerpc/20160803-hzb_web_1_3.gz', 
          '/data/logs/nginx/p.mogoroom.com.access.log-20160803.gz')]
        元组第一个元素为上传到OSS的对象名称
        元祖第二个元素为本地的文件路径
        '''
        nginx_project = self.init.config.options('nginx')
        files = []
        bucketobj = self.init.get_bucket(self.nginxbucket)
        for _p in nginx_project:
            _file = self.init.config.get('nginx',_p)

            #返回的格式是：mogo-logs-nginx/partnerpc/20160805____mogostore_60_91.gz 
            #由于这个函数会使用self.hostname获取本机名称
            #因此，返回的文件路径并不是OSS上的名称，要截取前面一段去查找OSS上的文件
            _yunfile = self._nginx_file_format(_file, _p) 
            _prefix_yunfile = _yunfile.split('____')[0]

            isexist = list( self.init.list_object(bucketobj, prefix=_prefix_yunfile) )
            if isexist:
                for i, _yf in isexist:
                    localfile = self._nginx_file_format(_yf.key, _p, download=True)
                    files.append((_yf.key, localfile))
            else:
                LOG.error(u'Nginx日志： {0}在OSS上不存在'.format(_prefix_yunfile))
                self.status = False
        return files

    def get_tomcat_files_fromoss(self):
        '''根据配置文件，返回需要从OSS上下载的文件列表
        返回格式：
        [('mogo-logs-tomcat/payapi/20160803-hzb_web_1_1.gz',
          '/logs/hzb_web_1_1/tomcat_payapi/catalina.out-20160803.gz')]
        元组第一个元素为上传到OSS的对象名称
        元祖第二个元素为本地的文件路径
        '''
        tomcat_project = self.init.config.options('tomcat')
        files = []
        bucketobj = self.init.get_bucket(self.tomcatbucket)
        for _p in tomcat_project:
            _dir = self.init.config.get('tomcat',_p).split('#')
            for _d in _dir:
                yunfile = self._tomcat_file_format(_d, _p)
                file = self._tomcat_file_format(yunfile, _p, download=True)
                yunfile_isexist = list( 
                    self.init.list_object(bucketobj, prefix=yunfile) )
                if yunfile_isexist:
                    files.append((yunfile_isexist[0][1].key,file))
                else:
                    LOG.error(u'Tomcat日志：{0}在OSS上不存在'.format(yunfile))
                    self.status = False
        return files

    def uploadnginx(self):
        '''上传服务器上昨天的nginx日志文件到OSS
        '''
        nginx_files = self.get_nginx_files()
        bucketobj = self.init.get_bucket(self.nginxbucket)
        for yunfile, localfile in nginx_files:
            self.init.put_object_from_file(bucketobj, yunfile, localfile)
            msg = u'上传Nginx日志：{0}到{1}成功'.format(localfile, yunfile)
            LOG.info(msg)
            print('{0} upload success'.format(localfile))

    def uploadtomcat(self):
        '''上传服务器上昨天的tomcat日志文件到OSS
        '''
        tomcat_files = self.get_tomcat_files()
        bucketobj = self.init.get_bucket(self.tomcatbucket)
        for yunfile, localfile in tomcat_files:
            self.init.put_object_from_file(bucketobj, yunfile, localfile)
            msg = u'上传Tomcat日志：{0}到{1}成功'.format(localfile, yunfile)
            LOG.info(msg)
            print('{0} upload success'.format(localfile))

    def getnginx(self):
        '''从OSS上下载昨天的nginx日志到本地并解压
        默认存放格式：/data/logs/nginx/p.mogoroom.com.access.log-20160803.gz
        '''
        nginx_files = self.get_nginx_files_fromoss()
        bucketobj = self.init.get_bucket(self.nginxbucket)
        for yunfile, localfile in nginx_files:
            _l = os.path.split(localfile)[0]
            if not os.path.isdir(_l):
                os.makedirs(_l)
            self.init.get_object_to_file(bucketobj, yunfile, localfile)
            self._unzipfile(localfile)
            msg = u'下载和解压Nginx日志：{1}到{0}成功'.format(localfile, yunfile)
            LOG.info(msg)
            print('{0} download success'.format(localfile))

    def gettomcat(self):
        '''从OSS上下载昨天的tomcat日志到本地并解压
        默认存放格式：/data/logs/tomcat/hzb_web_1_1/tomcat_payapi/catalina.out-20160803.gz
        '''
        tomcat_files = self.get_tomcat_files_fromoss()
        bucketobj = self.init.get_bucket(self.tomcatbucket)
        for yunfile, localfile in tomcat_files:
            _dir = os.path.split(localfile)[0]
            if not os.path.isdir(_dir):
                os.makedirs(_dir)
            self.init.get_object_to_file(bucketobj, yunfile, localfile)
            self._unzipfile(localfile)
            msg = u'下载和解压Tomcat日志：{1}到{0}成功'.format(localfile, yunfile)
            LOG.info(msg)
            print('{0} download success'.format(localfile))

    def _unzipfile(self, file):
        '''解压文件
        解压格式：/a/b/filename-20160803.gz 解压为 /a/b/filename
        '''
        g = gzip.GzipFile(mode='rb', fileobj=open(file, 'rb'))
        _pre = os.path.splitext(file)[0]
        utils.delete_files(_pre)
        uuid = utils.get_uuid()
        tf = '{0}____{1}.log'.format(_pre, uuid)
        open(tf, "wb").write(g.read())




    def main(self):
        self.uploadlog = os.getenv('MGOBJ_UPLOADLOG', 
            self.init.config.get('main','uploadlog'))
        if self.uploadlog == "1":
            self.uploadnginx()
        elif self.uploadlog == "2":
            self.uploadtomcat()
        elif self.uploadlog == "3":
            self.uploadnginx()
            self.uploadtomcat()
        elif self.uploadlog == '4':
            self.getnginx()
        elif self.uploadlog == '5':
            self.gettomcat()
        elif self.uploadlog == '6':
            self.getnginx()
            self.gettomcat()
        else:
            LOG.warning(u'配置文件没有启用任何日志传输')
            self.status = False



if __name__ == '__main__':
    try:
        UploadLogs().main()
    except Exception, err:
        print("Error: {0}".format(err), file=sys.stderr)
