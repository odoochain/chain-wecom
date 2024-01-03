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

    shortname =  fields.Char(string="Short name",)
    allow_wechat_website_auth = fields.Boolean(string="Allow WeChat website app login",default=False)

    wechat_website_auth_appid = fields.Char(string="WeChat website application ID",)

    wechat_website_auth_redirect_uri = fields.Char(string="WeChat website application redirect uri",)

    wechat_website_auth_lang = fields.Selection(
        string="WeChat website application ui language",
        selection=[
            ("cn","Chinese"),
            ("en","English"),
        ],
        default='cn')
