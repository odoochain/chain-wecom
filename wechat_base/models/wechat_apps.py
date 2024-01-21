# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class WeChatApplications(models.Model):
    """
    微信应用
    """
    _name = "wechat.applications"
    _description = "WeChat Applications"
    _order = "sequence"

    name = fields.Char(string="Name",copy=False,index=True,translate=True,)  # 应用名称
    app_type = fields.Selection(
        string='Application Type',
        required=True,
        selection=[('official_account', 'Official Account'), ('open_platform', 'Open platform')]
    )
    appid = fields.Char(string="Application Unique identification",copy=False,)  # 唯一标识
    secret = fields.Char(string="Application Secret",copy=False,)  # 应用密钥

    event_service_ids = fields.One2many(
        "wechat.event_service",
        "app_id",
        string="Event Service",
        domain="['|', ('active', '=', True), ('active', '=', False)]",
        context={"active_test": False},
    )

    sequence = fields.Integer(default=0, copy=True)