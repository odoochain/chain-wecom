# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _


class WecomServerApiError(models.Model):
    _inherit = "wechat.error_codes"


