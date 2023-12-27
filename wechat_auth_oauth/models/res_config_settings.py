# -*- coding: utf-8 -*-

from datetime import timedelta
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

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


    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    wechat_website_auth_appid = fields.Integer(related="company_id.wechat_website_auth_appid", readonly=False,)
    wechat_website_auth_redirect_uri = fields.Char(related="company_id.wechat_website_auth_redirect_uri", readonly=False,)
    wechat_website_auth_response_type = fields.Char(related="company_id.wechat_website_auth_response_type", readonly=True,store=True)
    wechat_website_auth_scope = fields.Char(related="company_id.wechat_website_auth_scope", readonly=True,store=True)
    wechat_website_auth_state = fields.Char(related="company_id.wechat_website_auth_state", readonly=True, store=True,default=_dwechat_website_auth_state)
    wechat_website_auth_lang = fields.Selection(related="company_id.wechat_website_auth_lang", readonly=False,)