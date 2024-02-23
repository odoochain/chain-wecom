# -*- coding: utf-8 -*-

import json

from odoo import _, api, fields, models, tools, Command
from odoo.exceptions import UserError
from odoo.osv import expression


class WechatComposeMessage(models.TransientModel):
    """
    撰写微信消息向导
    """

    _name = "wechat.compose.message"
    _description = "Wechat message composition wizard"
    _log_access = True

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
    openid = fields.Char(string="Wechat User Id",readonly=True,)

    # 内容
    subject = fields.Char("Subject", compute=False)
    template_id = fields.Many2one(
        "wechat.message_templates", "Use template", domain="[('model', '=', model)]"
    )
    wechat_template_id = fields.Char(string="Wechat template id",)
    jump_link = fields.Char(string="Template jump link")  # 模板跳转链接
    body = fields.Html("Contents",readonly=True)
    body_json = fields.Json("JSON Contents",readonly=True,default={})

    # 源
    author_id = fields.Many2one(
        "res.partner",
        "Author",
    )

    # 合成
    model = fields.Char("Related Document Model")
    res_id = fields.Integer("Related Document ID")
    record_name = fields.Char("Message Record Name")

    @api.model
    def get_record_data(self, values):
        result, subject = {}, False
        if values.get("partner_ids"):
            partner_ids = values.get("partner_ids")[0][2]
            openids = []
            for partner_id in partner_ids:
                partner = self.env["res.partner"].browse(partner_id)
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
            template =  self.env["wechat.message_templates"].browse(values.get("template_id"))
            result["wechat_template_id"] = template.template_id.template_id
            result["body"] = template.body_html


        result["subject"] = subject

        # res_id = values.get("res_id")
        # result["body_json"] = self.env["wechat.message_templates"].browse(values.get("res_id"))self.render_message(values.get("model"),res_id,xml_id,template_data)
        # print(result)
        return result


    def action_send_wenchat_message(self):
        if not self.partner_ids:
            raise UserError(_("No recipient found!"))
        if not self.template_id:
            raise UserError(_("Unbound WeChat message template!"))

        self._action_send_wenchat_message(auto_commit=False)

        return {"type": "ir.actions.act_window_close"}

    def _action_send_wenchat_message(self, auto_commit=False):
        """
        处理向导内容，并继续发送相关消息，如果需要，实时呈现任何模板模式。
        """
        model_description = self._context.get("model_description")
        model = self.env['ir.model']._get(self.model)
        model_name = model.model


        for wizard in self:
            res_ids = [wizard.res_id]
            template = self.env["wechat.message_templates"].browse(wizard.template_id.id)

            xml_id = template.get_external_id().get(wizard.template_id.id)
            template_data = template.body_html
            # record = model.
            try:
                rendered_body = self.env['mail.render.mixin']._render_template(
                    xml_id,
                    model_name,
                    res_ids,
                    engine='qweb_view',
                    add_context={
                        "company_name": ""
                        "partner_name": ""
                        "order_name": ""
                        "order_amount_total": ""
                        "sent_time": ""
                    },
                    post_process=True,
                )[wizard.res_id]
                print(rendered_body)
            except Exception as e:
                print("错误",str(e))


    def render_message(self, model, res_id, xml_id, template_data):
        """
        为 res_id 提供的文档记录生成向导的基于模板的值。这个方法是由 email_template 继承的，它将使用qweb模板生成一个更完整的字典
        """
        try:
            rendered_body = self.env['mail.render.mixin']._render_template(
                xml_id,
                model,
                [res_id],
                engine='qweb_view',
                add_context={},
                post_process=True,
            )[res_id]
            print(rendered_body)
        except Exception as e:
            print("错误",str(e))
        # body_json = json.loads(template_data)
        model = self.env[model]
        record = model.browse(res_id)
        print(record)

        return {}


