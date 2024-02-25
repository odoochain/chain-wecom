# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import (format_amount,format_datetime)
from datetime import datetime

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	def action_rfq_send_by_wechat(self):
		"""
		通过微信向供应商发送采购订单
		"""
		self.ensure_one()
		lang = self.env.context.get("lang")
		wechat_message_template = self.env.ref("wechat_message_purchase.wechat_message_template_edi_purchase_done", raise_if_not_found=False)

		ctx = {
			"default_model": "sale.order",
			"default_res_id": self.id,
			"default_partner_ids": self.partner_id.ids,
			"default_template_id": wechat_message_template.id if wechat_message_template else None,
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