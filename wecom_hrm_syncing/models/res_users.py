# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException


class ResUsers(models.Model):
    _inherit = "res.users"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Company employee",
        compute="_compute_company_employee",
        search="_search_company_employee",
        store=True,
    )  # 变更用户类型时，需要绑定用户，避免出现“创建员工”的按钮，故 store=True

    def set_wecom_user(self):
        """
        设置企业微信用户，当该用户已经关联employee时，将该employee的企业微信id信息写入到user中
        """
        if (
                self.employee_ids
                and self.employee_ids[0].is_wecom_user
                and self.employee_ids[0].wecom_userid
        ):
            self.write(
                {
                    "is_wecom_user": True,
                    # "is_wecom_notice": True,
                    "wecom_userid": self.employee_ids[0].wecom_userid,
                }
            )
        else:
            raise UserError(_("Please set wxwork employee for this user!"))
