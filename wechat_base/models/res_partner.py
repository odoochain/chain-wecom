# -*- coding: utf-8 -*-

from odoo import fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"

    is_wechat_user = fields.Boolean(
        string="WeChat user", default=False, readonly=True, store=True
    )
    wechat_open_platform_openid = fields.Char(
        string="WeChat Open Platform User OpenID",
        readonly=True,
        store=True,
    )
    wechat_official_account_openid = fields.Char(
        string="WeChat Officia Account User OpenID",
        readonly=True,
        store=True,
    )
    wechat_unionid = fields.Char(
        string="Unified identification of WeChat user", readonly=True, store=True
    )