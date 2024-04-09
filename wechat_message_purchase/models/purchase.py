# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import (format_amount,format_datetime)
from datetime import datetime

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	partner_type = fields.Selection(related="partner_id.company_type", string="Vendor Type",store=True)
	partner_contact = fields.Many2one('res.partner', string='Vendor Contact', domain="[('parent_id', '=', partner_id)]")



	def action_rfq_send_by_wechat(self):
		"""
		通过微信向供应商发送采购订单
		"""
		self.ensure_one()
		lang = self.env.context.get("lang")
		wechat_message_template = self.env.ref("wechat_message_purchase.wechat_message_template_edi_purchase_done", raise_if_not_found=False)

		ctx = {
			"default_model": "purchase.order",
			"default_res_id": self.id,
			"default_template_id": wechat_message_template.id if wechat_message_template else None,
		}
		if self.partner_type =="person":
			ctx.update({
				"default_partner_ids": self.partner_contact.ids,
			})
		else:
			ctx.update({
				"default_partner_ids": self.partner_contact.ids,
			})
		return {
			"type": "ir.actions.act_window",
			"view_mode": "form",
			"res_model": "wechat.compose.message",
			"views": [(False, "form")],
			"view_id": False,
			"target": "new",
			"context": ctx,
		}


	def get_vendor_name(self):
		"""
		获取供应商名称
		"""
		if self.partner_type=="company":
			return self.partner_id.name
		else:
			return self.partner_id.parent_id.name
			# if self.partner_id.parent_id:
			# 	return self.partner_id.parent_id.name
			# else:
			# 	return _("None")

	def get_vendor_contact_name(self):
		"""
		获取供应商联系人名称
		"""
		if self.partner_type=="company":
			return self.partner_contact.name
		else:
			return self.partner_id.name

	def get_amount_total(self):
		amount_total = format_amount(self.env, self.amount_total, self.currency_id)

		if "," in amount_total:
			amount_total = amount_total.replace(",","")
		return amount_total

	def get_sent_time(self):
		return format_datetime(self.env, datetime.now(), dt_format="yyyy-MM-dd HH:mm:ss", lang_code=self.env.lang)