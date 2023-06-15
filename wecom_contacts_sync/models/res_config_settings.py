# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # 自建应用
    self_built_app_id = fields.Many2one(
        related="company_id.self_built_app_id", readonly=False
    )
    self_built_app_agentid = fields.Integer(
        related="self_built_app_id.agentid", readonly=False
    )
    self_built_app_secret = fields.Char(
        related="self_built_app_id.secret", readonly=False
    )

    def generate_service(self):
        """
        生成服务
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "contacts":
            for record in self:
                if not record.contacts_app_id:
                    raise ValidationError(_("Please bind contact app!"))
                else:
                    record.contacts_app_id.with_context(code=code).generate_service()
        # super(ResConfigSettings, self).generate_service()

    def generate_parameters(self):
        """
        生成参数
        :return:
        """
        code = self.env.context.get("code")
        if bool(code) and code == "contacts":
            for record in self:
                if not record.contacts_app_id:
                    raise ValidationError(_("Please bind contact app!"))
                else:
                    record.contacts_app_id.with_context(code=code).generate_parameters()
        # super(ResConfigSettings, self).generate_parameters()
