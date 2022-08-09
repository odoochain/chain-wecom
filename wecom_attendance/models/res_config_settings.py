# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    attendance_app_id = fields.Many2one(string="Attendance AppId",
                                        related="company_id.attendance_app_id", readonly=False
                                        )
    attendance_agentid = fields.Integer(string="Attendance AgentId",
                                        related="attendance_app_id.agentid", readonly=False, default=3010011
                                        )

    attendance_secret = fields.Char(string="Attendance Secret",
                                    related="attendance_app_id.secret", readonly=False)

    def get_attendance_app_info(self):
        """
        获取应用信息
        :return:
        """
        app = self.env.context.get("app")
        for record in self:
            if app == "auth" and (
                record.attendance_app_id.agentid == 0 or record.attendance_app_id.secret == ""
            ):
                raise UserError(_("Auth application ID and secret cannot be empty!"))
            else:
                record.attendance_app_id.get_app_info()
        super(ResConfigSettings, self).get_app_info()
