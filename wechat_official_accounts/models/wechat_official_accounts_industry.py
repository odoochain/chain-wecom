# -*- coding: utf-8 -*-

import requests  # type: ignore
from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _


class WeChatOfficialAccountsIndustry(models.Model):
    """
    微信公众号行业
    """

    _name = "wechat.official_accounts.industry"
