# -*- coding: utf-8 -*-

import requests # type: ignore
from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _

def now(**kwargs):
    return datetime.now() + timedelta(**kwargs)

class WeChatApplications(models.Model):
    """
    微信应用
    """
    _name = "wechat.applications"
    _description = "WeChat Applications"
    _order = "sequence"

    name = fields.Char(string="Name",copy=False,index=True,translate=True,)  # 应用名称
    app_type = fields.Selection(
        string='Application Type',
        required=True,
        selection=[('official_account', 'Official Account'), ('open_platform', 'Open platform')]
    )
    appid = fields.Char(string="Application Unique identification",copy=False,)  # 唯一标识
    secret = fields.Char(string="Application Secret",copy=False,)  # 应用密钥
    access_token = fields.Char(string="Access Token", readonly=True, copy=False)
    access_token_expiration_time = fields.Datetime(
        string="Access Token Expiration Time", readonly=True, copy=False
    )

    event_service_ids = fields.One2many(
        "wechat.event_service",
        "app_id",
        string="Event Service",
        domain="['|', ('active', '=', True), ('active', '=', False)]",
        context={"active_test": False},
    )

    sequence = fields.Integer(default=0, copy=True)



    def get_access_token(self):
        """
        getAccessToken获
        https请求方式: GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
        ------------------------------------------------
        getStableAccessToken    仅支持 POST JSON 形式的调用
        https://api.weixin.qq.com/cgi-bin/stable_token
        """
        try:
            headers = {"content-type":"application/json"}
            get_access_token_url = "https://api.weixin.qq.com/cgi-bin/stable_token"
            json = {
                "grant_type":"client_credential",
                "appid":self.appid,
                "secret":self.secret,
                "force_refresh":False
            }
            if not self.access_token_expiration_time or (datetime.now() > self.access_token_expiration_time):
                response = requests.post(get_access_token_url,json=json,headers=headers).json()
        except Exception as e:
            print(str(e))
        else:
            # print(response)
            self.update({
                "access_token":response["access_token"],
                "access_token_expiration_time":now(hours=+2),
            })

    def cron_get_access_token(self):
        """
        自动任务定时获取应用token
        """
        for app in self:
            if app.appid & app.secret:
                app.get_access_token()
