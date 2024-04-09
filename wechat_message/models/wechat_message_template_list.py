# -*- coding: utf-8 -*-

import logging
import requests  # type: ignore
from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class WeChatMessageTemplateList(models.Model):
    """
    微信消息模板
    """

    _name = "wechat.message_template_list"
    _description = "WeChat Message Template List"


    name = fields.Char(string="Name", translate=False,compute="_compute_name",
        store=True,
        index=True,)
    template_id = fields.Char(string="Template Id", translate=False)
    title = fields.Char(string="Title", translate=False)

    @api.depends("template_id", "title")
    def _compute_name(self):
        for template in self:
            template.name = "%s-%s" % (template.template_id,template.title)

    _sql_constraints = [
        (
            "template_id_uniq",
            "unique (template_id)",
            _("Template Id must be unique !"),
        )
    ]

    @api.model
    def get_wechat_message_template_list(self):
        """
        """
        state = False
        msg= ""

        app = self.env["wechat.applications"].sudo().search([("app_type", "=", "official_account")], limit=1)
        api_url = "https://api.weixin.qq.com/cgi-bin/template/get_all_private_template?access_token=%s" % app.access_token
        try:
            response = requests.get(api_url).json()
        except Exception as e:
            print(str(e))
            state = False
            msg = str(e)
        else:
            templates = response["template_list"]
            for template in templates:
                t = self.sudo().search(
                    [
                        ("template_id", "=", template["template_id"])
                    ],
                    limit=1,
                )

                if not t:
                    t = self.create({
                        "template_id":template["template_id"],
                        "title":template["title"],
                    })
                else:
                    self.update({
                        "title":template["title"],
                    })
            state = True
            msg = _("Successfully obtained the template message list!")
        finally:
            return {"state": state, "msg": msg}