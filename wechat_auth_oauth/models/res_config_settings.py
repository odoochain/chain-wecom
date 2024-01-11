# -*- coding: utf-8 -*-

import os
from datetime import timedelta
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path  # type: ignore


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    def enable_wechat_oauth_login(self):
        """
        启用微信oauth的身份验证方式
        """
        type = self.env.context.get("type")
        if type =="click":
            provider_id = self.env["ir.model.data"]._xmlid_to_res_id("wechat_official_accounts.provider_wechat_one_click_login")
        if type =="scan":
            provider_id = self.env["ir.model.data"]._xmlid_to_res_id("wechat_website_application.provider_wechat_scan_code")

        provider =self.env["auth.oauth.provider"].browse(provider_id)
        provider.sudo().update({
            "enabled":True
        })