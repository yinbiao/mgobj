# mgobj



-----安装依赖包------
pip install -r requirements.txt 




-----command.py脚本说明-----

脚本用途：用于命令行操作OSS

Optional arguments:
  -h, --help             show this help message and exit

Auth:
  验证凭证

  --keyid                如果不提供使用配置文件config.conf配置的，但优先使用环境变量OSS_ACCESSID
  --keysecret            如果不提供使用配置文件config.conf配置的，但优先使用环境变量OSS_ACCESSKEYSECRET
  --endpoint             如果不提供使用配置文件config.conf配置的，但优先使用环境变量OSS_ENDPOINT

Bucket:
  桶操作

  --list-bucket          列出桶[python command.py --list-bucket]
  --create-bucket        创建桶 [python command.py --create-bucket bucketname]
  --delete-bucket        删除桶 [python command.py --delete-bucket bucketname]

Object:
  文件对象操作

  --list-object  [ ...]  查看桶文件 [python command.py --list-object
                         bucketname]（后面还可接前缀，列出指定文件）

  --delete-object        删除桶文件 [python command.py --delete-object bucketname
                         filename]

  --put-object           上传文件 [python command.py --put-object bucketname
                         云上的文件名称 本地文件路径]

  --get-object           下载文件 [python command.py --get-object bucketname
                         云上的文件名称 本地文件名称]

  --put-dir  [ ...]      上传文件夹 [python command.py --put-dir bucketname 本地文件夹路径
                         云上的文件夹路径（如果不设置，默认在bucket桶根目录下面）]

  --get-dir  [ ...]      下载文件夹 [python command.py --get-dir bucketname
                         云上的文件夹路径（如果不设置，默认为下载整个bucket文件）
                         本地存放目录（如果不设置，默认为存放在当前目录）]





-----mogo_logs_cron.py脚本说明-----

使用说明：

    1：定义config.conf配置文件
    2：可以设置环境变量（MGOBJ_UPLOADLOG）控制脚本的工作方式（优先级最高）

        1：上传nginx日志   2：上传tomcat日志  3：上传nginx和tomcat日志
        4：下载nginx日志   5：下载tomcat日志  6：下载nginx和tomcat日志

    3：执行命令：python mogo_logs_cron.py 或计划任务运行



脚本用途：nginx 和 tomcat日志的自动上传到OSS和下载到本地


    nginx日志会每天23:58分切割，然后此脚本将切割好的日志上传到OSS
    nginx日志存储在mogo-logs-nginx桶中

        上传到OSS的存储格式：桶名称/项目名称/时间-主机名称.gz
        下载到本地的存储格式：配置文件定义的父目录/项目名称/时间-主机名称.gz

    tomcat日志会每天23:58分切割，然后此脚本将切割好的日志上传到OSS，由于tomcat日志切割完后会被
    转移到/logs/目录下，因此上传tomcat的日志要从/logs目录下取
    tomcat日志存储在mogo-logs-tomcat桶中

        上传到OSS的存储格式：桶名称/项目名称/时间-主机名称.gz
        下载到本地的存储格式：配置文件定义的父目录/项目名称/时间-主机名称.gz



约束条件：

    1: 假设配置文件定义的日志路径为：/a/b/f1.log，
       那么压缩的日志文件格式必须为：/a/b/f1.log-20160803.gz
       否则会找不到文件。

    2: tomcat日志的上传路径固定在/logs/hzb_web_1_1/ 和 /logs/hzb_web_1_2/ 目录下

    3: nginx日志项目名称规范：
        消息包:           message
        payapi:          payapi
        租客APP和房东APP:  rpapp
        BS:              bs
        房东官网:          partnerpc
        租客官网:          renterpc

    4: tomcat日志项目名称规范：
        消息包:            message
        payapi:           payapi
        租客APP:           renter
        房东APP:           partner
        租客官网:           renterpc
        房东官网:           partnerpc


生产环境上的日志格式：

    nginx日志服务器：172.16.1.7 172.16.1.3

    /data/logs/nginx/msg.mogoroom.com.access.log       消息
    /data/logs/nginx/pay.api.mogoroom.com.access.log   PayApi
    /data/logs/nginx/app.api.mogoroom.com.access.log   租客APP和房东APP
    /data/logs/nginx/bs.mogoroom.com.access.log        BS
    /data/logs/nginx/p.mogoroom.com.access.log         房东官网
    /data/logs/nginx/www.mogoroom.com.access.log       租客官网

    
    tomcat日志服务器：172.16.1.1 172.16.1.2

    rentperpc(其他项目一样的存放格式):
    /logs/hzb_web_1_1/tomcat_renterpc/catalina.out-20160802.gz
    /logs/hzb_web_1_2/tomcat_renterpc/catalina.out-20160802.gz



