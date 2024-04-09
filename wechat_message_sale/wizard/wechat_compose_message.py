# -*- coding: utf-8 -*-

from odoo import models


class WechatComposeMessage(models.TransientModel):
    """
    撰写微信消息向导
    """
    _inherit = 'wechat.compose.message'


    