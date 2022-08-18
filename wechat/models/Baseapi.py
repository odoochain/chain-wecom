# -*- coding: utf-8 -*-
import json,requests

from soupsieve import DEBUG

from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException


class Baseapi(object):
    """ call企业微信基类 """
    def __init__(self):
        return

    def getAccessToken(self):
        raise NotImplementedError

    def refreshAccessToken(self):
        raise NotImplementedError

    def getSuiteAccessToken(self):
        raise NotImplementedError

    def getProviderAccessToken(self):
        raise NotImplementedError

    def httpcall(self, urltype, args=None):
        """
        call企业微信接口
        :param urltype:
        :param args:
        :return:
        """
        callurl = urltype[0]
        method = urltype[1]
        response = {}
        for retrycnt in range(0, 3):
            if method == 'GET':
                url = self.__makeurl(callurl)
                if args is not None:
                    url = self.__appendargs(url, args)
                response = self.__httpget(url)
            elif method == 'POST':
                pass

            else:
                raise ApiException(-1, "unknown method type")

            # 判断token是否过期
            if self.__checktoken(response.get('errcode')):
                continue

            else:
                break
        return self.__checkresponse(response)

    @staticmethod
    def __checkresponse(response):
        errcode = response.get('errcode')
        errmes = response.get('errmes')

        if errcode == '0':
            return response
        else:
            raise ApiException(errcode, errmes)

    @staticmethod
    def __makeurl(callurl):
        """
        拼接访问url
        :param callurl:
        :return:
        """
        baseurl = 'https://qyapi.weixin.qq.com'
        if callurl == '/':
            url = baseurl + '/'
        else:
            url = baseurl + '/' + callurl
        return url

    @staticmethod
    def __appendargs(url, args):
        """
        url添加args
        :param args:
        :return:
        """
        for key, value in args.items():
            if url.endswith('?'):
                url += ('&' + key + '=' + value)
            else:
                url += ('?' + key + '=' + value)
        return url

    def __httpget(self, url):
        realUrl = self.__appendToken(url)

        if DEBUG is True:
            print(realUrl)

        return requests.get(realUrl).json()

    def __appendToken(self, url):
        if 'SUITE_ACCESS_TOKEN' in url:
            return url.replace('SUITE_ACCESS_TOKEN', self.getSuiteAccessToken())
        elif 'PROVIDER_ACCESS_TOKEN' in url:
            return url.replace('PROVIDER_ACCESS_TOKEN', self.getProviderAccessToken())
        elif 'ACCESS_TOKEN' in url:
            return url.replace('ACCESS_TOKEN', self.getAccessToken())
        else:
            return url

    @staticmethod
    def __checktoken(errcode):
        if errcode == '40014' or errcode == '42001' or errcode == '42007' or errcode == '42009':
            return True
        else:
            return False
