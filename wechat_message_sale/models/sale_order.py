# -*- coding: utf-8 -*-


from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import (format_amount,format_datetime)
from datetime import datetime

class SaleOrder(models.Model):
	_inherit = "sale.order"

	def action_confirm_send_by_wechat(self):
		"""
		打开一个向导来发送微信消息，默认情况下加载相关的微信消息模板
		"""
		self.ensure_one()
		self.order_line._validate_analytic_distribution()
		lang = self.env.context.get("lang")
		wechat_message_template = self.env.ref("wechat_message_sale.wechat_message_template_sale_confirmation", raise_if_not_found=False)
		ctx = {
            "default_model": "sale.order",
            "default_res_id": self.id,
            "default_partner_ids": self.partner_id.ids,
            # "default_use_template": bool(mail_template),
            "default_template_id": wechat_message_template.id if wechat_message_template else None,
            # "default_composition_mode": "comment",
            # "mark_so_as_sent": True,
            # "default_email_layout_xmlid": "mail.mail_notification_layout_with_responsible_signature",
            "proforma": self.env.context.get("proforma", False),
            # "force_email": True,
            "model_description": self.with_context(lang=lang).type_name,
			"state":"sale",
        }
		return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "wechat.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }

	def _find_wechat_message_template(self):
		"""
		根据当前销售订单的状态获取相应的微信消息模板。

		如果SO已确认，我们将返回用于销售确认的邮件模板。
		否则，我们将返回报价电子邮件模板。

		:return: 基于当前状态的正确微信消息模板
		:rtype: record of `mail.template` or `None` if not found
		"""
		self.ensure_one()
		if self.env.context.get("proforma") or self.state not in ("sale", "done"):
			return self.env.ref("wechat_message_sale.wechat_message_template_sale", raise_if_not_found=False)
		else:
			return self._get_wechat_message_confirmation_template()

	def _get_wechat_message_confirmation_template(self):
		"""
		获取SO确认时发送的微信消息模板（或已确认的SO）。

		:return: `mail.template` record or None if default template wasn"t found
		"""
		return self.env.ref("wechat_message_sale.wechat_message_template_sale_confirmation", raise_if_not_found=False)

	def action_cancel_send_by_wechat(self):
		self.ensure_one()
		lang = self.env.context.get("lang")
		wechat_message_template = self.env.ref("wechat_message_sale.wechat_message_template_sale_cancellation", raise_if_not_found=False)

		if not wechat_message_template:
			raise UserError(_("The WeChat message template is not bound!"))

		ctx = {
            "default_model": "sale.order",
            "default_res_id": self.id,
            "default_partner_ids": self.partner_id.ids,
            "default_template_id": wechat_message_template.id if wechat_message_template else None,
            # "default_composition_mode": "comment",
            # "mark_so_as_sent": True,
            # "default_email_layout_xmlid": "mail.mail_notification_layout_with_responsible_signature",
            "proforma": self.env.context.get("proforma", False),
            # "force_email": True,
            "model_description": self.with_context(lang=lang).type_name,
			"state":"cancel",
        }
		action =  {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "wechat.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }
		return action

	def get_amount_total(self):
		""""""
		amount_total = format_amount(self.env, self.amount_total, self.pricelist_id.currency_id)
		# print(amount_total)
		# replace
		if "," in amount_total:
			amount_total = amount_total.replace(",","")
		return amount_total

	def get_sent_time(self):
		""""""
		# datetime.now()
		# return format_date(self.env, datetime.now(), date_format="medium",dt_format="yyyyMMddHHmmss", lang_code=self.env.lang)
		# print(datetime.now())
		# return format_date(self.env, datetime.now(), date_format="yyyy-MM-dd HH:mm:ss", lang_code=self.env.lang)
		return format_datetime(self.env, datetime.now(), dt_format="yyyy-MM-dd HH:mm:ss", lang_code=self.env.lang)
