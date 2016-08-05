# -*- coding: utf-8 -*-


from __future__ import print_function
from core import base
from core import utils
from core.utils import safe_decode as _
import logging
import argparse
import sys
import os

LOG = logging.getLogger(__name__)


class SelfHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=32,
                 width=None):
        super(SelfHelpFormatter, self).__init__(prog, indent_increment,
                                                     max_help_position, width)

    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(SelfHelpFormatter, self).start_section(heading)


class SelfArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(SelfArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2, ("Error: %(errmsg)s\nTry'%(mainp)s -h %(subp)s'"
                       " for more information.\n") %
                  {'errmsg': message.split(choose_from)[0],
                   'mainp': progparts[0],
                   'subp': progparts[2]})


class MgobjShell(object):

    def __init__(self):
        pass

    def get_base_parser(self):
        parser = SelfArgumentParser(
            description=_(u'云对象存储管理命令，目前支持阿里云OSS'),
            prog=_(u'命令'), 
            usage=_(u'%(prog)s [选项]'),
            argument_default=argparse.SUPPRESS,
            formatter_class=SelfHelpFormatter,)

        authgroup =  parser.add_argument_group('auth', _(u'验证凭证'))
        authgroup.add_argument(
            '--keyid',
            default=None,
            metavar='',
            help=_(u'如果不提供使用配置文件config.conf配置的, 但优先使用环境变量OSS_ACCESSID'))
        authgroup.add_argument(
            '--keysecret',
            default=None,
            metavar='',
            help=_(u'如果不提供使用配置文件config.conf配置的, 但优先使用环境变量OSS_ACCESSKEYSECRET'))
        authgroup.add_argument(
            '--endpoint',
            default=None,
            metavar='',
            help=_(u'如果不提供使用配置文件config.conf配置的, 但优先使用环境变量OSS_ENDPOINT'))

        bucketgroup =  parser.add_argument_group('bucket', _(u'桶操作'))
        bucketgroup.add_argument(
            '--list-bucket',
            action="store_true",
            default=None,
            help=_(u'列出桶[python command.py --list-bucket]'))
        bucketgroup.add_argument(
            '--create-bucket',
            nargs=1,
            default=None,
            metavar='',
            help=_(u'创建桶 [python command.py --create-bucket bucketname]'))
        bucketgroup.add_argument(
            '--delete-bucket',
            nargs=1,
            default=None,
            metavar='',
            help=_(u'删除桶 [python command.py --delete-bucket bucketname]'))

        objectgroup =  parser.add_argument_group('object', _(u'文件对象操作'))
        objectgroup.add_argument(
            '--list-object',
            nargs='+',
            default=None,
            metavar='',
            help=_(u'查看桶文件 [python command.py --list-object bucketname]（后面还可接前缀，列出指定文件）'))
        objectgroup.add_argument(
            '--delete-object',
            nargs=2,
            default=None,
            metavar='',
            help=_(u'删除桶文件 [python command.py --delete-object bucketname filename]'))
        objectgroup.add_argument(
            '--put-object',
            nargs=3,
            default=None,
            metavar='',
            help=_(u'上传文件 [python command.py --put-object bucketname 云上的文件名称 本地文件路径]'))
        objectgroup.add_argument(
            '--get-object',
            nargs=3,
            default=None,
            metavar='',
            help=_(u'下载文件 [python command.py --get-object bucketname 云上的文件名称 本地文件名称]'))
        objectgroup.add_argument(
            '--put-dir',
            nargs='+',
            default=None,
            metavar='',
            help=_(u'上传文件夹 [python command.py --put-dir bucketname 本地文件夹路径 云上的文件夹路径（如果不设置，默认在bucket桶根目录下面）]'))
        objectgroup.add_argument(
            '--get-dir',
            nargs='+',
            default=None,
            metavar='',
            help=_(u'下载文件夹 [python command.py --get-dir bucketname 云上的文件夹路径（如果不设置，默认为下载整个bucket文件） 本地存放目录（如果不设置，默认为存放在当前目录）]'))
        return parser

    def list_bucket(self, init):
        buckets = init.list_bucket()
        for item in buckets:
            print(item.name)

    def create_bucket(self, init, args):
        init.create_bucket(args[0])

    def delete_bucket(self, init, args):
        init.delete_bucket(args[0])

    def list_object(self, init, args):
        bucketobj = init.get_bucket(args[0])
        try:
            prefix = args[1]
        except:
            prefix = None
        if prefix is None:
            obj = init.list_object(bucketobj)
        else:
            obj = init.list_object(bucketobj, prefix=prefix)
        for i, obj_info in obj:
            print(utils.convert_timestamp(obj_info.last_modified), 
                obj_info.key,
                obj_info.size)

    def delete_object(self, init, args):
        bucketobj = init.get_bucket(args[0])
        filename = args[1]
        init.delete_object(bucketobj, filename)

    def put_object(self, init, args):
        bucketobj = init.get_bucket(args[0])
        yunfilename = args[1]
        filepath = args[2]
        init.put_object_from_file(bucketobj, yunfilename, filepath)

    def get_object(self, init, args):
        bucketobj = init.get_bucket(args[0])
        yunfilename = args[1]
        filepath = args[2]
        init.get_object_to_file(bucketobj, yunfilename, filepath)

    def put_dir(self, init, args):
        bucketobj = init.get_bucket(args[0])
        localdir = args[1]
        try:
            yundir = args[2]
        except:
            yundir = ''
        localfiles = utils.get_files(localdir, prefix=yundir)
        for f in localfiles:
            init.put_object_from_file(bucketobj, f[1], f[0])
            print("{0} uploaded".format(f[0]))

    def get_dir(self, init, args):
        bucketobj = init.get_bucket(args[0])
        objs = init.list_object(bucketobj)
        try:
            yundir = args[1]
        except:
            yundir = None
        try:
            localdir = args[2]
        except:
            localdir = None
        for i, obj_info in objs:
            if yundir is None:
                obj = obj_info.key
            elif obj_info.key.startswith(yundir):
                obj = obj_info.key
            else:
                obj = None

            if localdir is None:
                localdir = os.path.join(os.path.abspath(os.curdir),args[0])
            else:
                localdir = localdir[:-1] if localdir.endswith('/') else localdir
            if obj is not None and not obj.endswith('/'):
                localpath = os.path.join(localdir, obj)
                localpath_dir = os.path.split(localpath)[0]
                if not os.path.isdir(localpath_dir):
                    os.makedirs(localpath_dir)

                init.get_object_to_file(bucketobj, obj, localpath)

                print('{0} Download'.format(localpath))


    def main(self):
        parser = self.get_base_parser()
        args = parser.parse_args()
        init = base.Init(args.keyid, args.keysecret, args.endpoint)
        if args.list_bucket:
            self.list_bucket(init)
        elif args.create_bucket is not None:
            self.create_bucket(init, args.create_bucket)
        elif args.delete_bucket is not None:
            self.delete_bucket(init, args.delete_bucket)
        elif args.list_object is not None:
            self.list_object(init, args.list_object)
        elif args.delete_object is not None:
            self.delete_object(init, args.delete_object)
        elif args.put_object is not None:
            self.put_object(init, args.put_object)
        elif args.get_object is not None:
            self.get_object(init, args.get_object)
        elif args.put_dir is not None:
            self.put_dir(init, args.put_dir)
        elif args.get_dir is not None:
            self.get_dir(init, args.get_dir)





if __name__ == '__main__':

    try:
        '''我们使用了argparse模块，这个模块中使用sys.stdout.write作为输出，这个函数默认会
        使用file.encoding将字符串编码，一般为ascii，我们可以通过setdefaultencoding改变默认值。

        这个问题是python2.6的一个BUG
        '''
        reload(sys).setdefaultencoding('utf8')
        MgobjShell().main()
    except Exception, err:
        print("Error: {0}".format(err), file=sys.stderr)