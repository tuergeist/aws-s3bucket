import logging
import os
import tempfile
from pprint import pprint

import boto3 as boto3
import botocore
import requests as requests

logger = logging.getLogger('s3bucket')


def handle_unauthorized(func):
    def wrapped_try(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except botocore.exceptions.UnauthorizedSSOTokenError as error:
            logger.error(error)
            logger.error(f"You may want to run:  aws sso login --profile <profile name>")

    return wrapped_try


class S3Bucket:
    default_download_dir_prefix = 's3download_'

    def __init__(self, session, bucket_name):
        self._session = session
        self._bucket_name = bucket_name

        self.__s3 = session.resource('s3')
        self.__s3client = session.client('s3')
        self.__bucket = self.__s3.Bucket(bucket_name)

    @handle_unauthorized
    def simple_list(self, prefix: str = "", exclude: str = None):
        """
        List and filter object on the bucket
        :param prefix: optional filter prefix
        :param exclude: exclude names where "exclude" is in the name (somewhere)
        :return: list of filenames
        """
        objs = self.__bucket.objects.filter(Prefix=prefix)
        l = list()
        for my_bucket_object in objs:
            if exclude and exclude in my_bucket_object.key:
                continue
            l.append(my_bucket_object.key)
        return l

    @handle_unauthorized
    def list(self, prefix: str = None, suffix: str = None) -> list:
        """
        List and filter objects on the bucket
        returns list of dict {"name": str, "size": int}

        :param prefix: optional filter prefix
        :param suffix: optional filter suffix
        :return:
        """
        object_list = list()
        suffix_len: int = 0
        objs = self.__bucket.objects.filter(Prefix=prefix)
        if suffix:
            suffix_len = len(suffix)

        for my_bucket_object in objs:
            if not suffix or (suffix and my_bucket_object.key[-suffix_len:] == suffix):
                response = self.__s3client.head_object(Bucket=self._bucket_name, Key=my_bucket_object.key)
                name = my_bucket_object.key
                size = response['ContentLength']
                object_list.append({
                    "name": name,
                    "size": int(size)
                })
        return object_list

    @handle_unauthorized
    def download_to_dir(self, filename: str, tmpdir: str = ''):
        s3file = self.__s3client.get_object(Bucket=self._bucket_name, Key=filename)
        if not tmpdir:
            tmpdir = tempfile.mkdtemp(prefix=self.default_download_dir_prefix)

        logger.info(f"File {s3file.key} size is {s3file['ContentLength']}")
        target = os.path.join(tmpdir, os.path.basename(filename))
        if os.path.exists(target):
            logger.info(f"File {target} exists. skipping")
        else:
            self.__bucket.download_file(filename, target)
        return target

    def upload(self, upload_file, key: str, acl: str = 'public-read'):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_object
        :param upload_file:
        :param key:
        :param acl:
        :return:
        """
        response = self.__s3client.upload_file(upload_file, self._bucket_name, key, ExtraArgs={'ACL': acl})
        return response

    @staticmethod
    def download_public_file(url: str, save_path: str, chunk_size: int = 4096):
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size):
                    f.write(chunk)
        else:
            logger.warning(f"Did not download {url}. Response code was {r.status_code}")

    @staticmethod
    def default_bucket_factory(profile: str, bucket_name: str):
        session = boto3.Session(profile_name=profile)
        return S3Bucket(session, bucket_name)
