# -*- coding: utf-8 -*-

import hashlib
import json
import logging
from odoo import api, http, SUPERUSER_ID, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class WeChatOfficialAccounts(http.Controller):
    """
    公众号
    """
