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
    company_shortname = fields.Char(
        related="company_id.shortname", readonly=False, required=True
    )

    wechat_default_user_type = fields.Selection(
        string="Default registered user type for WeChat users",
        selection=[
            ("internal", "Internal User"),  # 内部用户
            ("portal", "Portal User"),  # 门户用户
            ("public", "Public User"),  # 公开用户
        ],
        default="portal",
        required=True,
    )
