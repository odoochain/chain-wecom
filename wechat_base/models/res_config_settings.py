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

    wechat_auth_signup_type = fields.Selection(
        string="How to create new users through WeChat registration",
        selection=[
            ("group", "User group"),  # 用户组
            ("template", "User template"),  # 用户模板
        ],
        default="group",
        required=True,
        config_parameter="wechat_auth_signup_type",
    )

    wechat_auth_signup_template_user_id = fields.Many2one(
        "res.users",
        string="Template user for new users created through WeChat registration",
        required=True,
        config_parameter="wechat_template_portal_user_id",
        default=5,
    )

    wechat_auth_signup_default_user_type = fields.Selection(
        string="Default registered user type for WeChat users",
        selection=[
            ("1", "Internal User"),  # 内部用户
            ("10", "Portal User"),  # 门户用户
            ("11", "Public User"),  # 公开用户
        ],
        default="10",
        required=True,
        config_parameter="wechat_auth_signup_default_user_type",
    )

    # 模块
    module_wechat_official_accounts = fields.Boolean("WeChat Official Accounts")
    module_wechat_web = fields.Boolean("WeChat Official Accounts H5 Website")
    module_wechat_website_application = fields.Boolean(
        "Website application WeChat login"
    )
    module_wechat_auth_oauth = fields.Boolean("WeChat OAuth2 Authentication")
