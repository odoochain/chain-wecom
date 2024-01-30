# -*- coding: utf-8 -*-

import requests  # type: ignore
from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _


class WeChatOfficialAccountsIndustry(models.Model):
    """
    微信公众号行业
    """

    _name = "wechat.official_accounts.industry"
    _description = "WeChat Official Accounts Industry"
    _order = "code"

    def _get_default_name(self):
        return "%s/%s" % (
            self.primary_industry,
            self.secondary_industry,
        )

    # display_name = fields.Char(compute="_compute_display_name")
    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True,
        translate=True,
    )
    primary_industry = fields.Char(
        string="Primary industry",
        translate=True,
    )  # 主营行业
    secondary_industry = fields.Char(
        string="Secondary industry",
        translate=True,
    )  # 副营行业
    code = fields.Integer(string="Industry Code", copy=False)

    _sql_constraints = [
        (
            "code_uniq",
            "unique (code)",
            _("code must be unique !"),
        )
    ]

    @api.depends("primary_industry", "secondary_industry")
    def _compute_name(self):
        for industry in self:
            industry.name = "%s/%s" % (
                industry.primary_industry,
                industry.secondary_industry,
            )
