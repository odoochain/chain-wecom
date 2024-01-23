# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


def now(**kwargs):
    return datetime.now() + timedelta(**kwargs)


class WeChatOfficialAccountsSubMenus(models.Model):
    """公众号菜单"""

    _name = "wechat.official_accounts.submenus"
    _description = "WeChat Official Accounts Menus"
    _order = "sequence"

    parent_menu_id = fields.Many2one(
        "wechat.official_accounts.menus",
        string="Parent menu",
        copy=False,
        ondelete="cascade",
        default=lambda self: self.env["wechat.official_accounts.menus"].id,
        required=True,
    )

    name = fields.Char(
        string="Name",
        copy=False,
        index=True,
        translate=True,
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
    url = fields.Char(
        string="Url",
        copy=False,
        translate=False,
    )
    key = fields.Char(
        string="Key",
        copy=False,
        translate=False,
    )
    sequence = fields.Integer(default=0, copy=True)
    active = fields.Boolean("Active", default=False)

    @api.model_create_multi
    def create(self, vals_list):
        parent_menu = None
        for vals in vals_list:
            if "parent_menu_id" in vals and vals.get("parent_menu_id"):
                parent_menu = self.env["wechat.official_accounts.menus"].browse(
                    vals.get("parent_menu_id")
                )
        res_ids = super(WeChatOfficialAccountsSubMenus, self).create(vals_list)
        submenus = self.search(
            [("parent_menu_id", "=", parent_menu.id), ("active", "=", True)]
        )
        if len(submenus) > 5 and parent_menu:
            raise ValidationError(
                _(
                    "Only 5 submenus can be created under the parent menu [%s]!"
                    % parent_menu.name,
                )
            )

        return res_ids
