# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderWechatMessage(models.TransientModel):
    _inherit = "wechat.compose.message"
    _description = "Sales Order Wechat message"

    def action_send_wenchat_message(self):
        res = super(SaleOrderWechatMessage, self).action_send_wenchat_message()
        if self.model == "sale.order" and self.state:
            sale_order = self.env[self.model].browse([self.res_id])
            sale_order.write({"state": self.env.context.get("state")})  # type: ignore
        return res
