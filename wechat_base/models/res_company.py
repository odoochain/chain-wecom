# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta
import random
import werkzeug.urls
import werkzeug.utils
import urllib
import datetime
import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    shortname =  fields.Char(string="Company Short Name",)

