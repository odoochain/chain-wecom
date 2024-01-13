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
	wechat_official_accounts_web_auth_lang = fields.Selection(
        string="The national and regional language version authorized by the WeChat official account webpage",
        selection=[
            ("zh_CN", "Chinese (Simplified)"),
            ("zh_TW", "Chinese (Traditional)"),
            ("en", "English"),
        ],
        default="zh_CN",
        required=True,
        config_parameter="wechat_official_accounts_web_auth_lang",
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


	def wechat_official_accounts_web_authorization(self):
		"""
		代公众号发起网页授权
		"""
		ICP = self.env["ir.config_parameter"].sudo()
		appid = ICP.get_param("wechat_official_accounts_developer_appid")
		secret = ICP.get_param("wechat_official_accounts_developer_secret")
		return_url = ICP.get_param("web.base.url")

		print(return_url)
		# 第一步：请求 CODE

		get_code_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=REDIRECT_URI&response_type=code&scope=SCOPE&state=STATE&component_appid=component_appid#wechat_redirect" % (appid)
