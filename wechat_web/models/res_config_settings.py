# -*- coding: utf-8 -*-

import os
from datetime import timedelta
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path  # type: ignore


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _wechat_web_state(self):
        code = ""
        for i in range(6):
            n = random.randint(0, 9)
            b = chr(random.randint(65, 90)).upper()
            s = chr(random.randint(97, 122)).upper()
            code += str(random.choice([n, b, s]))
        wechat_website_auth_state = self._context.get("wechat_website_auth_state")
        if wechat_website_auth_state:
            # 有效时间60分钟
            if (
                wechat_website_auth_state.write_date + timedelta(minutes=60)
                > fields.datetime.now()
            ):
                code = wechat_website_auth_state.value
            else:
                wechat_website_auth_state.write({"value": code})

        return code

    wechat_official_accounts_menu_data = fields.Char(
        string="Official Accounts Menu Data",
        default={},
        config_parameter="wechat_official_accounts_menu_data",
    )

    wechat_web_state = fields.Char(
        string="Official Accounts Menu Data",
        default=_wechat_web_state,
        config_parameter="wechat_web_state",
    )
