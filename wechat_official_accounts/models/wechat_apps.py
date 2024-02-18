# -*- coding: utf-8 -*-

import logging
import requests  # type: ignore
from datetime import datetime, timedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, Warning

_logger = logging.getLogger(__name__)


class WeChatApplications(models.Model):
    _inherit = "wechat.applications"

    primary_industry_id = fields.Many2one(
        "wechat.official_accounts.industry",
        string="Primary Industry",
    )  # 主营行业
    secondary_industry_id = fields.Many2one(
        "wechat.official_accounts.industry",
        string="Secondary Industry",
    )  # 副营行业

    @api.onchange("primary_industry_id", "secondary_industry_id")
    def _change_industry(self):
        if not self.primary_industry_id or not self.secondary_industry_id:
            pass
        elif self.primary_industry_id == self.secondary_industry_id:
            raise ValidationError(
                _(
                    "The primary and secondary industry cannot be the same!",
                )
            )

    def set_official_accounts_industry(self):
        """
        设置所属行业
        """
        headers = {"content-type": "application/json"}
        api_url = (
            "https://api.weixin.qq.com/cgi-bin/template/api_set_industry?access_token=%s"
            % self.access_token
        )
        json = {
            "industry_id1": self.primary_industry_id.code,
            "industry_id2": self.secondary_industry_id.code,
        }
        # print(json)
        data = {}
        try:
            response = requests.post(api_url, json=json, headers=headers).json()
        except Exception as e:
            print(str(e))
        else:
            if "errcode" in response and response["errcode"] != 0:
                error_msg = ""
                error_code = (
                    self.env["wechat.error_codes"]
                    .sudo()
                    .search_read(
                        domain=[("code", "=", response["errcode"])],
                        fields=["name"],
                    )
                )
                if error_code:
                    error_msg = error_code[0]["name"]
                else:
                    error_msg = _("unknown error")

                raise UserError(
                    _(
                        "Error code: %s, Error description: %s",
                        response["errcode"],
                        error_msg,
                    )
                )
            print(response)

    def get_official_accounts_industry(self):
        """
        获取设置的行业信息
        """
        api_url = (
            "https://api.weixin.qq.com/cgi-bin/template/get_industry?access_token=%s"
            % self.access_token
        )
        try:
            response = requests.get(api_url).json()
        except Exception as e:
            print(str(e))
        else:
            print(response)
            if "errcode" in response and response["errcode"] != 0:
                error_msg = ""
                error_code = (
                    self.env["wechat.error_codes"]
                    .sudo()
                    .search_read(
                        domain=[("code", "=", response["errcode"])],
                        fields=["name"],
                    )
                )
                if error_code:
                    error_msg = error_code[0]["name"]
                else:
                    error_msg = _("unknown error")

                raise UserError(
                    _(
                        "Error code: %s, Error description: %s",
                        response["errcode"],
                        error_msg,
                    )
                )
            industries = self.env["wechat.official_accounts.industry"].sudo()
            if "primary_industry" in response:
                primary_industry = response["primary_industry"]
                if (
                    "second_class" in primary_industry
                    and primary_industry["second_class"]
                ):
                    industry = industries.search(
                        [("secondary_industry", "=", primary_industry["second_class"])]
                    )
                    if industry:
                        self.update({"primary_industry_id": industry.id})

            if "secondary_industry" in response:
                secondary_industry = response["secondary_industry"]
                if (
                    "second_class" in secondary_industry
                    and secondary_industry["second_class"]
                ):
                    industry = industries.search(
                        [
                            (
                                "secondary_industry",
                                "=",
                                secondary_industry["second_class"],
                            )
                        ]
                    )
                    if industry:
                        self.update({"secondary_industry_id": industry.id})

            if primary_industry:
                industries = self.env["wechat.official_accounts.industry"]
