# -*- coding: utf-8 -*-

import os
from datetime import timedelta
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path  # type: ignore


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    wechat_official_accounts_menu_data = fields.Char(
        string="Official Accounts Menu Data",
        default={},
        config_parameter="wechat_official_accounts_menu_data",
    )
