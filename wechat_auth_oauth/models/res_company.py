# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
import random
import werkzeug.urls
import werkzeug.utils
import urllib
import datetime
import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    def _dwechat_website_auth_state(self):
        code = ''
        for i in range(6):
            n = random.randint(0, 9)
            b = chr(random.randint(65, 90)).upper()
            s = chr(random.randint(97, 122)).upper()
            code += str(random.choice([n, b, s]))
        wechat_website_auth_state = self._context.get('wechat_website_auth_state')
        if wechat_website_auth_state:
            # 有效时间60分钟
            if wechat_website_auth_state.write_date + timedelta(minutes=60) > fields.datetime.now():
                code = wechat_website_auth_state.value
            else:
                wechat_website_auth_state.write({'value': code})

        return code

    wechat_website_auth_appid = fields.Integer(string="WeChat website application ID",)
    wechat_website_auth_redirect_uri = fields.Char(string="WeChat website application redirect uri",)
    wechat_website_auth_response_type = fields.Char(string="WeChat website application response type",default='code')
    wechat_website_auth_scope = fields.Char(string="WeChat website application authorization scope",default='snsapi_login')
    wechat_website_auth_state = fields.Char(string="WeChat website application state")
    wechat_website_auth_lang = fields.Selection(
        string="WeChat website application ui language",
        selection=[
            ("cn","Chinese"),
            ("en","English"),
        ],
        default='cn')
