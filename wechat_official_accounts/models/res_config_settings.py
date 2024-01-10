# -*- coding: utf-8 -*-

import io
from PIL import Image
from odoo import models, fields, api, _,tools
from odoo.modules.module import get_resource_path
from odoo.tools.image import base64_to_image,binary_to_image
from random import randrange

class ResConfigSettings(models.TransientModel):
	_inherit = "res.config.settings"

	company_id = fields.Many2one(
		"res.company",
		string="Company",
		required=True,
		default=lambda self: self.env.company,
	)
	social_wechat_official_accounts = fields.Binary(
		related="company_id.social_wechat_official_accounts", readonly=False
	)

	wechat_official_accounts_developer_appid = fields.Char(
		string="WeChat Official accounts Developer ID",
		config_parameter="wechat_official_accounts_developer_appid",
	)
	wechat_official_accounts_developer_secret= fields.Char(
		string="WeChat Official accounts Developer secret key",
		config_parameter="wechat_official_accounts_developer_secret",
	)


	@api.onchange('social_wechat_official_accounts')
	def _onchange_social_wechat_official_accounts(self):
		"""
		更新微信公众号二维码
		"""
		img_path = get_resource_path('wechat_official_accounts', 'static/src/img', "qrcode.png")
		with tools.file_open(img_path, 'rb') as f:
			# original = Image.open(f)
			# new_image = Image.new('RGBA', original.size)
			new_image = base64_to_image(self.social_wechat_official_accounts)
			# print(new_image)
			# image_io = io.BytesIO()
			new_image.save(img_path, format="PNG")