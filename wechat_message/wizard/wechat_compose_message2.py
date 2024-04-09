# -*- coding: utf-8 -*-

import json
import xmltodict
import requests  # type: ignore

from odoo import _, api, fields, models, tools, Command
from odoo.exceptions import UserError
from odoo.osv import expression


def _reopen(self, res_id, model, context=None):
    # save original model in context, because selecting the list of available
    # templates requires a model in context
    context = dict(context or {}, default_model=model)
    return {
        "type": "ir.actions.act_window",
        "view_mode": "form",
        "res_id": res_id,
        "res_model": self._name,
        "target": "new",
        "context": context,
    }


class WechatComposeMessage(models.TransientModel):
    """
    撰写微信消息向导
    """

    _name = "wechat.compose.message"
    _inherit = "mail.composer.mixin"
    _description = "Wechat message composition wizard"
    # _log_access = True

    @api.model
    def default_get(self, fields):
        result = super(WechatComposeMessage, self).default_get(fields)
        if "model" in fields and "model" not in result:
            result["model"] = self._context.get("active_model")
        if "res_id" in fields and "res_id" not in result:
            result["res_id"] = self._context.get("active_id")
        if set(fields) & set(
            ["model", "res_id", "partner_ids", "record_name", "subject"]
        ):
            result.update(self.get_record_data(result))
        if "create_uid" in fields and "create_uid" not in result:
            result["create_uid"] = self.env.uid

        filtered_result = dict(
            (fname, result[fname]) for fname in result if fname in fields
        )
        return filtered_result

    def _partner_ids_domain(self):
        return expression.OR(
            [
                [("is_wechat_user", "=", True)],
                [("type", "!=", "private")],
                [("id", "in", self.env.context.get("default_partner_ids", []))],
            ]
        )

    # 接受者
    partner_ids = fields.Many2many(
        "res.partner",
        "wechat_compose_message_res_partner_rel",
        "wizard_id",
        "partner_id",
        "Additional Contacts",
        domain=_partner_ids_domain,
        readonly=True,
    )
    openid = fields.Char(
        string="Wechat User Id",
        readonly=True,
        store=True,
    )

    # 内容
    subject = fields.Char("Subject", compute=False)
    template_id = fields.Many2one(
        "wechat.message_templates", "Use template", domain="[('model', '=', model)]"
    )
    wechat_template_id = fields.Char(
        string="Wechat template id", required=True,store=True,
    )
    jump_link = fields.Char(string="Template jump link")  # 模板跳转链接
    body = fields.Text("Contents", compute=False, readonly=True,store=True,)

    # 源
    author_id = fields.Many2one(
        "res.partner",
        "Author",
    )

    # 合成
    model = fields.Char("Related Document Model")
    res_id = fields.Integer("Related Document ID")
    record_name = fields.Char("Message Record Name")

    # Overrides of mail.render.mixin
    @api.depends("model")
    def _compute_render_model(self):
        for composer in self:
            composer.render_model = composer.model

    @api.model
    def get_record_data(self, values):
        result, subject = {}, False
        if values.get("partner_ids"):
            partner_ids = values.get("partner_ids")[0][2]
            openids = []
            for partner_id in partner_ids:
                partner = self.env["res.partner"].browse(partner_id)
                if not partner.wechat_official_account_openid:
                    raise UserError(_("The current customer is not a WeChat user!"))
                openids.append(partner.wechat_official_account_openid)
            result["openid"] = ",".join(openids)

        if values.get("model") and values.get("res_id"):
            doc_name_get = (
                self.env[values.get("model")].browse(values.get("res_id")).name_get()
            )
            result["record_name"] = doc_name_get and doc_name_get[0][1] or ""
            subject = tools.ustr(result["record_name"])
            result["jump_link"] = self.env[values.get("model")].get_base_url() + self.env[values.get("model")].browse(values.get("res_id")).get_portal_url()  # type: ignore

        if values.get("template_id"):
            template = self.env["wechat.message_templates"].browse(
                values.get("template_id")
            )
            result["wechat_template_id"] = template.template_id.template_id
            template_body = self.render_message_body(values.get("model"),values.get("res_id"),template.body_html)
            result["body"] = template_body


        result["subject"] = subject
        return result


    def action_send_wenchat_message(self):
        """Used for action button that do not accept arguments."""
        self._action_send_wenchat_message()
        return {"type": "ir.actions.act_window_close"}

    def _action_send_wenchat_message(self):
        """
        """
        data_dict = self.get_message_json(self.body)
        if not data_dict:
            raise UserError(_("There is an error in the content of the WeChat message template!"))

        data_dict.update({  # type: ignore
            "touser":self.openid,
            "template_id":self.wechat_template_id,
            "url":self.jump_link,
        })

        try:
            headers = {"content-type": "application/json"}
            app = self.env["wechat.applications"].sudo().search([("app_type", "=", "official_account")], limit=1)
            api_url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % app.access_token
            response = requests.post(api_url, json=data_dict, headers=headers).json()
        except Exception as e:
            print(str(e))
        else:
            if response["errcode"] == 0:
                params = {
                    "title": _("Success"),
                    "message": _("Successfully sent WeChat message!"),
                    "sticky": False,  # 延时关闭
                    "className": "bg-success",
                }
                action = {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": params["title"],
                        "type": "success",
                        "message": params["message"],
                        "sticky": params["sticky"],
                    },
                }
                # print(action)
                return action
            elif response["errcode"] == 42001:
                # access_token 超时,重启获取 Token
                pass
            else:
                error_msg = ""
                error_code = (
                    self.env["wechat.error_codes"]
                    .sudo()
                    .search_read(
                        domain=[("code", "=", response["errcode"])],
                        fields=["name"],
                    )
                )
                if error_code:
                    error_msg = error_code[0]["name"]
                else:
                    error_msg = _("unknown error")

                raise UserError(
                    _(
                        "Error code: %s, Error description: %s;Error details: %s",
                        response["errcode"],
                        error_msg,
                        response["errmsg"],
                    )
                )


    def call_wechat_api(self, data):
        """
        调用微信API
        """
        try:
            headers = {"content-type": "application/json"}
            app = self.env["wechat.applications"].sudo().search([("app_type", "=", "official_account")], limit=1)
            api_url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % app.access_token
            response = requests.post(api_url, json=data, headers=headers).json()
        except Exception as e:
            print(str(e))
            return False
        finally:
            return response["errcode"]

    def render_message_body(self, model, res_id, body):
        """"""
        records = self.env[model].browse([res_id])
        body = self.env['mail.render.mixin']._render_template(body, records._name, records.ids)
        body_contents = body[res_id]
        if "\xa0" in body_contents:
            body_contents = body_contents.replace(u'\xa0', u'')
        return body_contents

    def get_message_json(self,body):
        """"""
        body_json = False
        try:
            body_json = json.loads(body)
        except Exception as e:
            print(str(e))
            return False
        finally:
            return body_json
