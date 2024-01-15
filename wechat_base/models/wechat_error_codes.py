# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class WecomServerApiError(models.Model):
    """
    https://developers.weixin.qq.com/doc/oplatform/Return_codes/Return_code_descriptions_new.html
    """

    _name = "wechat.error_codes"
    _description = "WeChat public error code"
    _order = "sequence"

    name = fields.Char(
        "Error description",
        required=True,
        readonly=True,
    )
    code = fields.Integer(
        "Error code",
        required=True,
        readonly=True,
    )
    code_text = fields.Char(
        "Error code text",
        required=True,
        readonly=True,
    )

    sequence = fields.Integer(default=0)
