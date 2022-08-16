# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    # 素材库
    material_app_id = fields.Many2one(
        "wecom.apps",
        string="Material Application",
        # required=True,
        # default=lambda self: self.env.company,
        # domain="[('company_id', '=', current_company_id)]",
        domain="[('company_id', '=', current_company_id)]",
    )
