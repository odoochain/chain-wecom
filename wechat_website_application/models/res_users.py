# -*- coding: utf-8 -*-
import urllib
from urllib import parse
from odoo import models, api, _
from odoo.exceptions import AccessDenied


class ResUsers(models.Model):
    _inherit = "res.users"

