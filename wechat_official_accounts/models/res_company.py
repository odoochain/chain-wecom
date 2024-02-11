# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class ResCompany(models.Model):
    _inherit = "res.company"

    social_wechat_official_accounts = fields.Binary(
        string="WeChat Official Accounts QR Code"
    )  #  default=_default_qrcode

    def _get_social_media_links(self):
        social_media_links = super()._get_social_media_links()
        social_media_links.update({
            'social_wechat_official_accounts': self.social_wechat_official_accounts
        })
        return social_media_links

