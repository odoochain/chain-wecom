# -*- coding: utf-8 -*-
import urllib
from urllib import parse
from odoo import models, api, _
from odoo.exceptions import AccessDenied


class ResUsers(models.Model):
    _inherit = "res.users"

    # ---------------------
    # 微信验证
    # ---------------------
    @api.model
    def wechat_auth_oauth(self, provider, params):
        """
        微信 OAuth2 验证

        :param provider: OAuth2 程序提供者的ID
        :param params: {'access_token': '', 'expires_in': 7200, 'refresh_token': '', 'openid': '', 'scope': 'snsapi_login', 'unionid': ''}
        :return
        """
        wechat_open_endpoint = "https://open.weixin.qq.com/connect/qrconnect"

        wechat_providers = (
            self.env["auth.oauth.provider"]
            .sudo()
            .search(
                [
                    ("id", "=", provider),
                ]
            )
        )

        ICP = self.env["ir.config_parameter"].sudo()
        default_user_company = ICP.get_param("wechat_default_user_company")
        default_user_type = ICP.get_param("wechat_default_user_type")

        # 用户类型
        group_id = self.env["ir.model.data"]._xmlid_to_res_id("base.group_portal")
        if default_user_type == "1":
            group_id = self.env["ir.model.data"]._xmlid_to_res_id("base.group_user")
        elif default_user_type == "10":
            group_id = self.env["ir.model.data"]._xmlid_to_res_id("base.group_portal")
        elif default_user_type == "11":
            group_id = self.env["ir.model.data"]._xmlid_to_res_id("base.group_public")

        # print("当前时间", current_time)
        # {'openid': '', 'nickname': 'ð\x9f\x8c\x88å½©è\x99¹å·¥ä½\x9cå®¤', 'sex': 0, 'language': '', 'city': '', 'province': '', 'country': '', 'headimgurl': '', 'privilege': [], 'unionid': ''}

        # 查询用户是否存在
        SudoUser = self.sudo()
        oauth_openid = params["openid"]
        oauth_user = SudoUser.search(
            [
                "|",
                ("wechat_openid", "=", params["openid"]),
                ("wechat_unionid", "=", params["unionid"]),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ],
            limit=1,
        )

        if not oauth_user:
            # 创建用户
            nickname = params["nickname"].encode("ISO-8859-1").decode("utf-8")
            oauth_user = SudoUser.create(
                {
                    "name": nickname,
                    "login": params["openid"],
                    "password": self.env["wechat.tools.security"].random_passwd(8),
                    "share": False,
                    "active": True,
                    "groups_id": [(6, 0, [group_id])],
                    "company_ids": [(6, 0, [int(default_user_company)])],
                    "company_id": int(default_user_company),
                    # 以下为微信字段
                    "is_wechat_user": True,
                    "wechat_openid": params["openid"],
                    "wechat_nickname": nickname,
                    "wechat_unionid": params["unionid"],
                }
            )
        print(oauth_user.id)
        if oauth_user:
            print("验证成功--------")
            return (self.env.cr.dbname, oauth_user.login, oauth_openid)  # type: ignore
        else:
            return AccessDenied

    def _check_credentials(self, password, env):
        # password为微信的用户 openid
        try:
            return super(ResUsers, self)._check_credentials(password, env)  # type: ignore
        except AccessDenied:
            res = self.sudo().search(
                [("id", "=", self.env.uid), ("wechat_openid", "=", password)]
            )
            if not res:
                raise
