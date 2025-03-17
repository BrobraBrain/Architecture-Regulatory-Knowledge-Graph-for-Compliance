# -*- coding: utf-8 -*-
"""
@Author  : #######
@Time    : #######
@Email   : #######
"""
import time
from functools import wraps

import os
import oss2


class OssOperate(object):
    """
    oss相关操作
    """

    def __init__(self, env: str = "prod"):
        self.__access_key_id = '###############'
        self.__access_key_secret = '###############'
        self.endpoint = '###############' if env == 'prod' else '###############'
        self.bucket = '###############'
        self.bucket_dir = 'generate'
        self.sava_path = '/tmp'

    def download_file(self, oss_uri: str, save_path: str = None):
        """
        简单下载
        :param oss_uri: oss上文件目录加文件名称，如'generate/a.png'
        :param save_path: 文件需要保存的目录
        """
        save_path = self.sava_path if save_path is None else save_path
        filename = oss_uri.split('/')[-1]
        save_path = os.path.join(save_path, filename)
        bucket_obj = self.get_bucket_obj()
        bucket_obj.get_object_to_file(oss_uri, save_path)
        return save_path

    def put_file(self, oss_uri: str, file_path: str = None):
        """
        简单上传
        :param oss_uri: oss上文件目录加文件名称，如'generate/a.png'
        :param file_path: 待上传文件的绝对路径
        """
        bucket_obj = self.get_bucket_obj()
        bucket_obj.put_object_from_file(oss_uri, file_path)

    def get_bucket_obj(self):
        auth = oss2.Auth(self.__access_key_id, self.__access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        return bucket

