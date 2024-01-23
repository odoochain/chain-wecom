# -*- coding: utf-8 -*-

import json
import logging
import xml.etree.cElementTree as ET
from lxml import etree
import sys
from odoo.addons.wecom_api.api.wecom_msg_crtpt import WecomMsgCrypt  # type: ignore
from odoo import http, models, fields, _
from odoo.http import request
from odoo.http import Response

_logger = logging.getLogger(__name__)
