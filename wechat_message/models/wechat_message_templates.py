# -*- coding: utf-8 -*-

import requests  # type: ignore
from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _


def now(**kwargs):
    return datetime.now() + timedelta(**kwargs)


class WeChatMessageTemplates(models.Model):
    """
    微信消息模板
    """

    _name = "wechat.message_templates"
    _inherit = ["mail.render.mixin"]
    _description = "WeChat Message Templates"
    # _order = "sequence"

    @api.model
    def default_get(self, fields):
        res = super(WeChatMessageTemplates, self).default_get(fields)

        if res.get("model"):
            res["model_id"] = self.env["ir.model"]._get(res.pop("model")).id
        return res

    name = fields.Char(string="Name", required=True, translate=True)
    subject = fields.Char(string="Subject")
    # code = fields.Char(string="Code", required=True)
    model_id = fields.Many2one("ir.model", string="Applied to")
    model = fields.Char("Model", related="model_id.model")
    description = fields.Text(
        "Template description",
        translate=True,
        help="This field is used for internal description of the template's usage.",
    )
