# -*- coding: utf-8 -*-

import os
from datetime import timedelta
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_resource_path  # type: ignore


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    wechat_website_app = fields.Many2one(
        "wechat.applications",
        string="Website Application",
        domain="[('app_type', '=', 'open_platform')]",
        config_parameter="wechat_website_app",
    )

    wechat_website_auth_appid = fields.Char(
        string="WeChat Website Application ID",
        related="wechat_website_app.appid",
        readonly=False,
    )
    wechat_website_auth_secret = fields.Char(
        string="WeChat Website Application secret key",
        related="wechat_website_app.secret",
        readonly=False,
    )

    wechat_website_app_event_service = fields.One2many(
        related="wechat_website_app.event_service_ids",
        string="WeChat Website Application Event Service",
        readonly=False,
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

    # wechat_open_platform_event_service_ids = fields.One2many(
    #     "wechat.event_service",
    #     "config",
    #     string="Open Platform Events Service",
    #     domain="[('service_type', '=', 'open_platform')",
    #     context={"active_test": False},
    # )

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
