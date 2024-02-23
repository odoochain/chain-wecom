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

    template_id = fields.Many2one(
        "wechat.message_template_list", string="Wechat Message Template Id"
    )
    jump_link = fields.Char(string="Template jump link")  # 模板跳转链接
    body_html = fields.Text(
        string="Body",
        render_engine="qweb",
        translate=True,
        prefetch=True,
        sanitize=False,
        default={},
    )
    body_json = fields.Char(string="Body", translate=True, default={})


# {
#                 'thing4':{'value':{{ object.company_id.name }}},
#                 'thing5':{'value':{{ object.partner_id.name }}},
#                 'character_string1':{'value': {{ object.name }}},
#                 'amount2':{'value': <t t-out="format_amount(object.amount_total, object.currency_id) or ''">$ 10.00</t>},
#                 'time3':{'value': <t t-out="format_datetime(object.create_date, tz='UTC', dt_format=&quot;yyyyMMdd'T'HHmmss'Z'&quot;)"/> }
# "time3":{"value": {{ format_datetime(dt=object.create_date, tz='UTC', dt_format=&quot;yyyyMMdd'T'HHmmss'Z'&quot;, lang_code=object.env.lang)}}}"amount2":{"value": {{ object.get_amount_total() }}},
# "time3":{"value": {{ object.get_sent_time() }}},
#             }
