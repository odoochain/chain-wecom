# -*- coding: utf-8 -*-

import os
from datetime import timedelta
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path  # type: ignore


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_wechat_message_sale = fields.Boolean(
        "Send sales quotations and order messages to WeChat users."
    )
    module_gooderp_wechat_message_sell = fields.Boolean(
        "Send sales quotations and order messages to WeChat users.(For GoodErp)"
    )

    module_wechat_message_purchase = fields.Boolean(
        "Send purchase orders, tenders, and agreements to WeChat users."
    )

    module_gooderp_wechat_message_buy = fields.Boolean(
        "Send purchase orders, tenders, and agreements to WeChat users.(For GoodErp)"
    )
