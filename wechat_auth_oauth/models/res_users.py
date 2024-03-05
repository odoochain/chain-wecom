# -*- coding: utf-8 -*-

from ast import literal_eval
import urllib
from urllib import parse
from odoo import models, api, _
from odoo.exceptions import AccessDenied
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
        official_account_openid
        open_platform_openid
        :param provider: OAuth2 程序提供者的ID
        :param params: {"access_token": "", "expires_in": 7200, "refresh_token": "", "openid": "", "scope": "snsapi_login", "unionid": ""}
        :return
        """
        # print(provider, params)
        values = {}
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
            values.update({
                "wechat_open_platform_openid":params["openid"]
            })
        elif wechat_official_accounts_endpoint in wechat_providers["auth_endpoint"]:
            auth_type="one_click"
            values.update({
                "wechat_official_account_openid":params["openid"]
            })

        if auth_type=="":
            return AccessDenied

        # 查询用户是否存在
        oauth_id = ""
        domain = []
        if "unionid" in params:
            oauth_id = params["unionid"]
            domain=[
                ("wechat_unionid", "=", params["unionid"]),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ]
            values.update({
                "login": params["unionid"],
                "wechat_unionid": params["unionid"],
            })
        elif "openid" in params:
            oauth_id = params["openid"]
            domain=[
                "|",
                ("wechat_open_platform_openid", "=", params["openid"]),
                ("wechat_official_account_openid", "=", params["openid"]),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ]
            values.update({
                "login": params["openid"],
            })

        oauth_user = self.sudo().search(
            domain,
            limit=1,
        )

        if not oauth_user:
            # 创建用户
            # 用户信息
        # {"openid": "", "nickname": "ð\x9f\x8c\x88å½©è\x99¹å·¥ä½\x9cå®¤", "sex": 0, "language": "", "city": "", "province": "", "country": "", "headimgurl": "", "privilege": [], "unionid": ""}
            user_company = ICP.get_param("wechat_default_user_company")
            nickname = params["nickname"].encode("ISO-8859-1").decode("utf-8")
            try:
                values.update({
                    "name": nickname,
                    "password": self.env["wechat.tools.security"].random_passwd(8),
                    "share": False,
                    "active": True,
                    "company_id": int(user_company),
                    "company_ids": [(6, 0, [int(user_company)])],
                    # "notification_type": "inbox",
                    "notification_type": "email",
                    # 以下为微信专有字段
                    "is_wechat_user": True,
                    "wechat_nickname": nickname,
                    "wechat_access_token": params["access_token"],
                    "wechat_access_token_expires_in": now(hours=+2),
                    "wechat_refresh_token_expires_in": now(days=+30),
                    "wechat_refresh_token": params["refresh_token"],
                })
                # print("values---",values)
            except Exception as e:
                print("values更新错误:",str(e))
            oauth_user = self._wechat_signup_create_user(values,ICP)


        if oauth_user:
            if oauth_user.wechat_open_platform_openid is False and auth_type=="scan":
                oauth_user.update({
                    "wechat_open_platform_openid":params["openid"]
                })
            elif oauth_user.wechat_official_account_openid is False and auth_type=="one_click":
                oauth_user.update({
                    "wechat_official_account_openid":params["openid"]
                })


            partner = {
                "is_wechat_user":True
            }
            if "wechat_open_platform_openid" in values:
                partner.update({
                    "wechat_open_platform_openid": values["wechat_open_platform_openid"]
                })
            if "wechat_official_account_openid" in values:
                partner.update({
                    "wechat_official_account_openid": values["wechat_official_account_openid"]
                })
            if "wechat_unionid" in values:
                partner.update({
                    "wechat_unionid": values["wechat_unionid"]
                })

            try:
                oauth_user.partner_id.update(partner)
            except Exception as e:
                print("partner 错误:",str(e))

            # gooderp 的 `partner.address` 模型
            if self.check_gooderp_installed():
                try:
                    domain = ["|",("wechat_open_platform_openid","=",params["openid"]),("wechat_official_account_openid","=",params["openid"])]
                    pa = self.env["partner.address"].sudo().search(domain,limit=1)  # type: ignore
                    # print(g_partner)
                    if not pa: # type: ignore
                        partner.update({    # type: ignore
                            "contact": oauth_user.name, # type: ignore
                        })

                        pa_id = pa.create(partner)
                        oauth_user.partner_address_id = pa_id # type: ignore
                    else:
                        oauth_user.partner_address_id.sudo().update(partner) # type: ignore
                    oauth_user.partner_address_id = pa_id.id # type: ignore
                except Exception as e:
                    print("GoodErp partner错误:",str(e))

            return (self.env.cr.dbname, oauth_user.login, oauth_id)  # type: ignore
        else:
            return AccessDenied

    def _wechat_signup_create_user(self,values,ICP):
        """
        微信注册新用户
        """
        auth_signup_type = ICP.get_param("wechat_auth_signup_type")
        try:
            if auth_signup_type=="group":
                return self._wechet_create_user_from_group(values,ICP)
            elif auth_signup_type=="template":
                return self._wechet_create_user_from_template(values,ICP)
            else:
                return False
        except Exception as e:
            print("错误：",str(e))

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
            print("从用户组创建新用户,错误:",str(e))
            return False

    def _wechet_create_user_from_template(self,values,ICP):
        """
        从模板创建新用户
        """
        user_template = ICP.get_param("wechat_template_portal_user_id")
        template_user_id = literal_eval(self.env["ir.config_parameter"].sudo().get_param("wechat_template_portal_user_id", "False"))    # type: ignore
        template_user = self.browse(template_user_id)
        if not template_user.exists():
            raise ValueError(_("Wechat Signup: invalid template user"))
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
            print("从模板创建新用户,错误:",str(e))
            return False

    def _check_credentials(self, password, env):
        # -----------------------------------------------------
        # 如果 unionid 存在，password为微信的用户 unionid
        # 如果 unionid 不存在，password为微信的用户 openid
        # -----------------------------------------------------
        try:
            return super(ResUsers, self)._check_credentials(password, env)  # type: ignore
        except AccessDenied:
            res = self.sudo().search(
                [
                    ("id", "=", self.env.uid),
                    "|",
                    "|",
                     ("wechat_unionid", "=", password),
                     ("wechat_open_platform_openid", "=", password),
                     ("wechat_official_account_openid", "=", password)
                     ]
            )
            if not res:
                raise


    def check_gooderp_installed(self):
        """
        检查GoodErp 是否已安装
        """
        module = self.env["ir.module.module"].sudo().search([("name", "=", "gooderp_wechat_base")])
        if not module or module.state != "installed":   # type: ignore
            return False
        else:
            return True