# -*- coding: utf-8 -*-

from ast import literal_eval
import urllib
from urllib import parse
from odoo import models, api, _
from odoo.exceptions import AccessDenied
from odoo.tools.misc import ustr
from odoo.addons.auth_signup.models.res_partner import SignupError, now

class ResUsers(models.Model):
    _inherit = "res.users"

    # ---------------------
    # 检索并登录与提供程序和已验证的访问令牌对应的微信用户
    # ---------------------
    @api.model
    def wechat_auth_oauth(self, provider, params):
        """
        微信 OAuth2 验证

        :param provider: OAuth2 程序提供者的ID
        :param params: {'access_token': '', 'expires_in': 7200, 'refresh_token': '', 'openid': '', 'scope': 'snsapi_login', 'unionid': ''}
        :return
        """
        ICP = self.env["ir.config_parameter"].sudo()
        wechat_open_endpoint = "https://open.weixin.qq.com/connect/qrconnect"
        wechat_official_accounts_endpoint = "https://open.weixin.qq.com/connect/oauth2/authorize"

        auth_type= ""
        wechat_providers = (
            self.env["auth.oauth.provider"]
            .sudo()
            .search(
                [
                    ("id", "=", provider),
                ]
            )
        )
        if wechat_open_endpoint in wechat_providers["auth_endpoint"]:
            auth_type="scan"
        elif wechat_official_accounts_endpoint in wechat_providers["auth_endpoint"]:
            auth_type="one_click"

        if auth_type=="":
            return AccessDenied

        # 查询用户是否存在
        # oauth_openid = params["openid"]
        oauth_unionid = params["unionid"]
        oauth_user = self.sudo().search(
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
            # 用户信息
        # {'openid': '', 'nickname': 'ð\x9f\x8c\x88å½©è\x99¹å·¥ä½\x9cå®¤', 'sex': 0, 'language': '', 'city': '', 'province': '', 'country': '', 'headimgurl': '', 'privilege': [], 'unionid': ''}
            user_company = ICP.get_param("wechat_default_user_company")
            nickname = params["nickname"].encode("ISO-8859-1").decode("utf-8")
            values = {
                "name": nickname,
                "login": params["unionid"],
                "password": self.env["wechat.tools.security"].random_passwd(8),
                "share": False,
                "active": True,
                "company_ids": [(6, 0, [int(user_company)])],
                "company_id": int(user_company),
                # 以下为微信专有字段
                "is_wechat_user": True,
                "wechat_openid": params["openid"],
                "wechat_nickname": nickname,
                "wechat_unionid": params["unionid"],
                "wechat_access_token": params["access_token"],
                "wechat_access_token_expires_in": now(hours=+2),
                "wechat_refresh_token_expires_in": now(days=+30),
                "wechat_refresh_token": params["refresh_token"],
            }
            oauth_user = self._wechat_signup_create_user(values,ICP)

        if oauth_user:
            print("验证成功--------")
            return (self.env.cr.dbname, oauth_user.login, oauth_unionid)  # type: ignore
        else:
            return AccessDenied


    def _wechat_signup_create_user(self,values,ICP):
        """
        微信注册新用户
        """
        auth_signup_type = ICP.get_param("wechat_auth_signup_type")

        if auth_signup_type=="group":
            return self._wechet_create_user_from_group(values,ICP)
        elif auth_signup_type=="template":
            return self._wechet_create_user_from_template(values,ICP)
        else:
            return False

    def _wechet_create_user_from_group(self,values,ICP):
        """
        从用户组创建新用户
        """
        user_type = ICP.get_param("wechat_auth_signup_default_user_type")
        group_id = self.env["ir.model.data"]._xmlid_to_res_id("base.group_portal")
        if user_type == "1":
            group_id = self.env["ir.model.data"]._xmlid_to_res_id("base.group_user")
        elif user_type == "10":
            group_id = self.env["ir.model.data"]._xmlid_to_res_id("base.group_portal")
        elif user_type == "11":
            group_id = self.env["ir.model.data"]._xmlid_to_res_id("base.group_public")
        values.update({
            "groups_id": [(6, 0, [group_id])]
        })
        try:
            return self.sudo().create(values)
        except Exception as e:
            # print("从用户组创建新用户,错误:",str(e))
            return False

    def _wechet_create_user_from_template(self,values,ICP):
        """
        从模板创建新用户
        """
        user_template = ICP.get_param("wechat_template_portal_user_id")
        template_user_id = literal_eval(self.env['ir.config_parameter'].sudo().get_param('wechat_template_portal_user_id', 'False'))
        template_user = self.browse(template_user_id)
        if not template_user.exists():
            raise ValueError(_('Wechat Signup: invalid template user'))
        try:
            groups = template_user.groups_id
            group_ids = []
            for group in groups:
                group_ids.append(group.id)
            values.update({
                "groups_id": [(6, 0, group_ids)]
            })

            return self.sudo().create(values)
            # return template_user.with_context(no_reset_password=True).copy(values)
        except Exception as e:
            # copy may failed if asked login is not available.
            # print("从模板创建新用户,错误:",str(e))
            return False


    def _check_credentials(self, password, env):
        # password为微信的用户 unionid
        try:
            return super(ResUsers, self)._check_credentials(password, env)  # type: ignore
        except AccessDenied:
            # print(self.env.uid)
            res = self.sudo().search(
                [("id", "=", self.env.uid), ("wechat_unionid", "=", password)]
            )
            # print(res)
            if not res:
                raise
