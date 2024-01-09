# -*- coding: utf-8 -*-

from datetime import timedelta
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    # company_shortname = fields.Char(
    #     related="company_id.shortname", readonly=False, required=True
    # )

    wechat_default_user_company = fields.Many2one(
        "res.company",
        string="Default registered company for WeChat users",
        required=True,
        default=lambda self: self.env.company,
        config_parameter="wechat_default_user_company",
    )

    wechat_default_user_type = fields.Selection(
        string="Default registered user type for WeChat users",
        selection=[
            ("1", "Internal User"),  # 内部用户
            ("10", "Portal User"),  # 门户用户
            ("11", "Public User"),  # 公开用户
        ],
        default="10",
        required=True,
        config_parameter="wechat_default_user_type",
    )

    # 模块
    module_wechat_official_accounts = fields.Boolean(
        "WeChat Official accounts"
    )
    module_wechat_website_application = fields.Boolean(
        "Website application WeChat login"
    )
    module_wechat_auth_oauth = fields.Boolean(
        "WeChat OAuth2 Authentication"
    )
