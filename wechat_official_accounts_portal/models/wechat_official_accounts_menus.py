# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


def now(**kwargs):
    return datetime.now() + timedelta(**kwargs)


class WeChatOfficialAccountsMenus(models.Model):
    """公众号菜单"""

    _name = "wechat.official_accounts.menus"
    _description = "WeChat Official Accounts Menus"
    _order = "sequence"

    app_id = fields.Many2one(
        "wechat.applications",
        string="Application",
        copy=False,
        ondelete="cascade",
        default=lambda self: self.env["wechat.applications"].id,
        required=True,
    )
    submenu_ids = fields.One2many(
        "wechat.official_accounts.submenus",
        "parent_menu_id",
        string="Submenu",
        domain="['|', ('active', '=', True), ('active', '=', False)]",
        context={"active_test": False},
    )
    name = fields.Char(
        string="Menu Name",
        copy=False,
        index=True,
        translate=True,
        required=True,
    )
    menu_type = fields.Selection(
        string="Menu Type",
        required=True,
        selection=[
            ("view", "Web Type"),
            ("click", "Click Type"),
            ("miniprogram", "Mini Program type"),
        ],
    )
    appid = fields.Char(
        string="Mini Program Application ID",
        copy=False,
        translate=False,
    )
    pagepath = fields.Char(
        string="Page path of Mini Program",
        copy=False,
        translate=False,
    )
    route = fields.Char(string="Route", translate=False)
    url = fields.Char(
        string="Url", copy=False, translate=False, compute="_default_url", store=True
    )
    key = fields.Char(
        string="Key",
        copy=False,
        translate=False,
    )
    sequence = fields.Integer(default=1, copy=True)
    active = fields.Boolean("Active", default=False)

    @api.depends("route")
    def _default_url(self):
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")
        for menu in self:
            if menu.menu_type == "view":
                menu.url = base_url + menu.route

    @api.model_create_multi
    def create(self, vals_list):
        app = None
        for vals in vals_list:
            if "app_id" in vals and vals.get("app_id"):
                app = self.env["wechat.applications"].browse(vals.get("app_id"))
        res_ids = super(WeChatOfficialAccountsMenus, self).create(vals_list)
        menus = self.search([("active", "=", True)])
        if len(menus) > 3 and app:
            raise ValidationError(
                _(
                    "The number of menus with [%s] cannot be greater than 3!"
                    % app.name,
                )
            )

        return res_ids
