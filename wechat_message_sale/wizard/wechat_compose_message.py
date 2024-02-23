# -*- coding: utf-8 -*-

from odoo import models


class WechatComposeMessage(models.TransientModel):
    """
    撰写微信消息向导
    """
    _inherit = 'wechat.compose.message'


    def action_send_wenchat_message(self):
        if self.model == 'sale.order':
            pass
        return super(WechatComposeMessage, self).action_send_wenchat_message()