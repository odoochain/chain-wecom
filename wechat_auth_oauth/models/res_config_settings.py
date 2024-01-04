# -*- coding: utf-8 -*-

import os
from datetime import timedelta
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path  # type: ignore


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _dwechat_website_auth_state(self):
        code = ""
        for i in range(6):
            n = random.randint(0, 9)
            b = chr(random.randint(65, 90)).upper()
            s = chr(random.randint(97, 122)).upper()
            code += str(random.choice([n, b, s]))
        wechat_website_auth_state = self._context.get("wechat_website_auth_state")
        if wechat_website_auth_state:
            # 有效时间60分钟
            if (
                wechat_website_auth_state.write_date + timedelta(minutes=60)
                > fields.datetime.now()
            ):
                code = wechat_website_auth_state.value
            else:
                wechat_website_auth_state.write({"value": code})

        return code

    allow_wechat_website_auth = fields.Boolean(
        string="Allow WeChat website app login",
        default=False,
        config_parameter="allow_wechat_website_auth",
    )

    wechat_website_auth_appid = fields.Char(
        string="WeChat website application ID",
        config_parameter="wechat_website_auth_appid",
    )
    wechat_website_auth_secret = fields.Char(
        string="WeChat website application secret key",
        config_parameter="wechat_website_auth_secret",
    )
    wechat_website_auth_state = fields.Char(
        string="Maintain the state of requests and callbacks",
        readonly=True,
        store=True,
        config_parameter="wechat_website_auth_state",
    )

    wechat_website_auth_qrcode_display_method = fields.Selection(
        string="How to display the login QR code of WeChat website",
        selection=[
            ("embedded", "Embedded"),
            ("dialog", "Dialog"),
        ],
        default="embedded",
        required=True,
        config_parameter="wechat_website_auth_qrcode_display_method",
    )

    wechat_website_auth_lang = fields.Selection(
        string="WeChat website application ui language",
        selection=[
            ("cn", "Chinese"),
            ("en", "English"),
        ],
        default="cn",
        required=True,
        config_parameter="wechat_website_auth_lang",
    )

    wechat_website_auth_qrcode_style = fields.Selection(
        string="QR Code Color Style",
        selection=[
            ("black", "Black"),
            ("white", "White"),
        ],
        default="black",
        required=True,
    )

    wechat_website_auth_qrcode_width = fields.Integer(
        string="QR Code Width (px)",
        default=280,
        config_parameter="wechat_website_auth_qrcode_width",
    )
    wechat_website_auth_qrcode_hide_title = fields.Boolean(
        string="Hide QR code title",
        default=False,
        config_parameter="wechat_website_auth_qrcode_hide_title",
    )
    wechat_website_auth_qrcode_info_width = fields.Integer(
        string="QR code information text width (px)",
        default=280,
        config_parameter="wechat_website_auth_qrcode_info_width",
    )
    wechat_website_auth_qrcode_hide_status_icon = fields.Boolean(
        string="Hide QR code status icon",
        default=False,
        config_parameter="wechat_website_auth_qrcode_hide_status_icon",
    )
    wechat_website_auth_qrcode_status_text_align = fields.Selection(
        string="Horizontal alignment of QR code status",
        selection=[
            ("left", "Left"),
            ("center", "Center"),
            ("right", "Right"),
        ],
        default="center",
        required=True,
        config_parameter="wechat_website_auth_qrcode_status_text_align",
    )

    @api.onchange(
        "wechat_website_auth_qrcode_width",
        "wechat_website_auth_qrcode_hide_title",
        "wechat_website_auth_qrcode_info_width",
        "wechat_website_auth_qrcode_hide_status_icon",
        "wechat_website_auth_qrcode_status_text_align",
    )
    def _on_change_wechat_website_auth_qrcode_css(self):
        """
        变更二维码样式时，更新css文件
        """
        css_path = get_resource_path("wechat_auth_oauth", "static", "str", "legacy", "public", "css", "wehcat_qrcode.css")  # type: ignore

        if not os.path.exists(css_path):
            os.makedirs(css_path)

        ICP = self.env["ir.config_parameter"].sudo()
        css_code = """.impowerBox .qrcode {width: %spx;}
.impowerBox .title {display: %s;}
.impowerBox .info {width: %spx;}
.status_icon {display: %s;}
.impowerBox .status {text-align: %s;}""" % (
            ICP.get_param("wechat_website_auth_qrcode_width"),
            "none"
            if bool(ICP.get_param("wechat_website_auth_qrcode_hide_title"))
            else "block",
            ICP.get_param("wechat_website_auth_qrcode_info_width"),
            "none"
            if bool(ICP.get_param("wechat_website_auth_qrcode_hide_status_icon"))
            else "block",
            ICP.get_param("wechat_website_auth_qrcode_status_text_align"),
        )
        # 清空文件并写入新内容
        with open(css_path, "w") as fp:
            fp.write(css_code)
            fp.close()
