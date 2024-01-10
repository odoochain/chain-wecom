# -*- coding: utf-8 -*-

import os
from datetime import timedelta
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path  # type: ignore


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    def enable_wechat_oauth_login(self):
        """
        """
        type = self.env.context.get("type")
        print(type)