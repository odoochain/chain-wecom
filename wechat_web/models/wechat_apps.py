# -*- coding: utf-8 -*-

import json
import requests  # type: ignore
from odoo import api, fields, models, SUPERUSER_ID, _


class WeChatApplications(models.Model):
    """
    微信应用
    """

    _inherit = "wechat.applications"

    official_accounts_menu_ids = fields.One2many(
        "wechat.official_accounts.menus",
        "app_id",
        string="Official Accounts Menus",
        domain="['|', ('active', '=', True), ('active', '=', False)]",
        context={"active_test": False},
    )

    official_accounts_menu_data = fields.Json(
        string="Official Accounts Menus Data", default={}
    )

    def download_official_accounts_menu(self):
        """
        下载公众号菜单数据
        """

    def generate_official_accounts_menu_data(self):
        """
        生成公众号菜单数据
        """
        # TODO 待处理子菜单
        json = {"button": []}
        for menu in self.official_accounts_menu_ids:
            if menu.active:
                res = {
                    "name": menu.name,
                    "type": menu.menu_type,
                    "sub_button": [],
                }
                if menu.menu_type == "view":
                    res.update({"url": menu.url})
                if menu.menu_type == "click":
                    res.update({"key": menu.key})
                if menu.menu_type == "miniprogram":
                    res.update(
                        {
                            "url": menu.url,
                            "appid": menu.appid,
                            "pagepath": menu.pagepath,
                        }
                    )
                json["button"].append(res)

        # self.write({"official_accounts_menu_data": json})
        self.official_accounts_menu_data = json
        return {"type": "ir.actions.client", "tag": "reload"}  # 刷新页面

    def upload_official_accounts_menu(self):
        """
        上传公众号菜单数据
        """
        api_url = (
            "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s"
            % self.access_token
        )

        # json = json.dumps(self.official_accounts_menu_data, ensure_ascii=False).encode(
        #     "utf-8"
        # )
        json_data = json.dumps(
            self.official_accounts_menu_data, ensure_ascii=False
        ).encode(
            "utf-8"
        )  # 将dict数据转化成json数据
        print(json_data, type(json_data))

        headers = {"content-type": "application/json"}
        response = requests.post(api_url, data=json_data, headers=headers).json()
        print(response)
