# -*- coding: utf-8 -*-

import logging
import datetime
import werkzeug.utils
import urllib
from odoo import _, api, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    def generate_parameters_by_code(self, code):
        """
        根据code生成参数
        :param code:
        :return:
        """
        if code == "auth":
            ir_model_data = self.env["ir.model.data"]
            auth_redirect_uri = ir_model_data.get_object_reference(
                "wecom_auth_oauth", "wecom_app_config_authentication_auth_redirect_uri"
            )[1]
            qr_redirect_uri = ir_model_data.get_object_reference(
                "wecom_auth_oauth", "wecom_app_config_authentication_qr_redirect_uri"
            )[1]
            vals_list = [
                auth_redirect_uri,
                qr_redirect_uri,
            ]

            for id in vals_list:
                app_config_id = self.env["wecom.app_config"].search([("id", "=", id)])
                app_config = (
                    self.env["wecom.app_config"]
                    .sudo()
                    .search([("app_id", "=", self.id), ("key", "=", app_config_id.key)]) # type: ignore
                )
                if not app_config:
                    app_config = (
                        self.env["wecom.app_config"]
                        .sudo()
                        .create(
                            {
                                "name": app_config_id.name,
                                "app_id": self.id,   # type: ignore
                                "key": app_config_id.key,
                                "ttype": app_config_id.ttype,
                                "value": app_config_id.value,
                                "description": app_config_id.description,
                            }
                        )
                    )
                else:
                    app_config.sudo().write(
                        {
                            "name": app_config_id.name,
                            "value": app_config_id.value,
                            "description": app_config_id.description,
                        }
                    )
        super(WeComApps, self).generate_parameters_by_code(code)     # type: ignore

    # ————————————————————————————————————
    # 设置认证应用配置
    # ————————————————————————————————————
    def set_oauth_provider_wecom(self):
        web_base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        auth_redirect_uri = None
        qr_redirect_uri = None
        if len(self.app_config_ids) > 0:     # type: ignore
            for record in self.app_config_ids:   # type: ignore
                if record["key"] == "auth_redirect_uri":
                    auth_redirect_uri = record
                if record["key"] == "qr_redirect_uri":
                    qr_redirect_uri = record

                # print(auth_redirect_uri, qr_redirect_uri)
            new_auth_redirect_uri = (
                urllib.parse.urlparse(web_base_url).scheme   # type: ignore
                + "://"
                + urllib.parse.urlparse(web_base_url).netloc     # type: ignore
                + urllib.parse.urlparse(auth_redirect_uri.value).path    # type: ignore
            )
            new_qr_redirect_uri = (
                urllib.parse.urlparse(web_base_url).scheme   # type: ignore
                + "://"
                + urllib.parse.urlparse(web_base_url).netloc     # type: ignore
                + urllib.parse.urlparse(qr_redirect_uri.value).path  # type: ignore
            )

            # 设置应用参数中的回调链接地址
            auth_redirect_uri.write({"value": new_auth_redirect_uri})    # type: ignore
            qr_redirect_uri.write({"value": new_qr_redirect_uri})    # type: ignore

            auth_endpoint = "https://open.weixin.qq.com/connect/oauth2/authorize"
            qr_auth_endpoint = "https://open.work.weixin.qq.com/wwopen/sso/qrConnect"

            try:
                providers = (
                    self.env["auth.oauth.provider"]
                    .sudo()
                    .search(["|", ("enabled", "=", True), ("enabled", "=", False),])
                )
            except Exception:
                providers = []

            for provider in providers:
                if auth_endpoint in provider["auth_endpoint"]:
                    provider.write(
                        {
                            # "client_id": client_id,
                            "validation_endpoint": auth_redirect_uri,
                            "enabled": True,
                        }
                    )
                if qr_auth_endpoint in provider["auth_endpoint"]:
                    provider.write(
                        {
                            # "client_id": client_id,
                            "validation_endpoint": qr_redirect_uri,
                            "enabled": True,
                        }
                    )
