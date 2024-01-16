# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class WecomServerApiError(models.Model):
    """
    https://developers.weixin.qq.com/doc/oplatform/Return_codes/Return_code_descriptions_new.html
    """

    _name = "wechat.error_codes"
    _description = "WeChat public error code"
    _order = "code"

    name = fields.Char(
        "Error description",
        required=True,
        readonly=True,
        translate=True
    )
    code = fields.Integer(
        "Error code",
        required=True,
        readonly=True,
    )
    code_text = fields.Char(
        "Error code text",
        compute="_compute_code_text",
        store=True,
        readonly=True,
    )

    @api.depends("code")
    def _compute_code_text(self):
        for code in self:
            code.code_text = str(code.code)