# -*- coding: utf-8 -*-

from odoo import fields, models


class AuthOAuthProvider(models.Model):
    _inherit = 'auth.oauth.provider'

    name = fields.Char(string='Provider name', required=True, translate=True)
    description = fields.Char(string="OAuth description", translate=True)