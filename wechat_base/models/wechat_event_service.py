# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class WechatEventService (models.Model):
    """
    微信事件服务
    """
    _name = "wechat.event_service"
    _description = "WeChat event service"

    app_id = fields.Many2one(
        "wechat.applications",
        string="Application",
        copy=False,
        ondelete="cascade",
        default=lambda self: self.env["wechat.applications"].id,
        # domain="[('company_id', '=', company_id)]",
        required=True,
    )
    name = fields.Char(string="Service Name", required=True, translate=True)
    service_type = fields.Selection(
        string='Service Type',
        required=True,
        selection=[('official_account', 'Official Account'), ('open_platform', 'Open platform')]
    )

    route = fields.Char(string="Route", required=True, translate=False)
    url = fields.Char(
        string="URL",
        store=True,
        readonly=True,
        compute="_default_url",
        copy=False,
    )  # 回调服务地址
    token = fields.Char(string="Token", copy=False)  # Token用于计算签名
    aeskey = fields.Char(string="AES Key", copy=False)  # 用于消息内容加密
    description = fields.Text(string="Description", translate=True, copy=True)
    active = fields.Boolean("Active", default=False)

    @api.depends("route")
    def _default_url(self):
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")
        for service in self:
            service.url = base_url + service.route
