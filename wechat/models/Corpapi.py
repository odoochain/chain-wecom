# -*- coding: utf-8 -*-
from .Baseapi import *


CORP_API_TYPE = {
            'GET_ACCESS_TOKEN': ['/cgi-bin/gettoken', 'GET'],
            'GET_USER_INFO_BY_CODE': ['/cgi-bin/user/getuserinfo?access_token=ACCESS_TOKEN', 'GET']
}

class Corpapi(Baseapi):
    def __init__(self, corpid, secret):
        self.corpid = corpid
        self.secret = secret
        self.access_token = None

    def getAccessToken(self):
        if self.access_token is None:
            self.refreshaccesstoken()

    def refreshaccesstoken(self):
        self.httpcall(
            CORP_API_TYPE['GET_ACCESS_TOKEN'],
            {
                'corpid': self.corpid,
                'secret': self.secret
            }
        )

