# -*- coding: utf-8 -*-

# !参考 \addons\auth_oauth\controllers\main.py

import logging
import json
import werkzeug.urls
import werkzeug.utils
from werkzeug.exceptions import BadRequest

from odoo import api, http, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied
from odoo.http import request, Response
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home # type: ignore
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string    # type: ignore
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url    # type: ignore

_logger = logging.getLogger(__name__)

class OAuthLogin(Home):

    def list_providers(self):
        try:
            providers = request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])
        except Exception:
            providers = []
        for provider in providers:
            if "https://open.weixin.qq.com/connect/qrconnect" in provider["auth_endpoint"]:
                # 判断是微信登录

                return_url = request.httprequest.url_root + 'wechat_auth_oauth'
                state = self.get_state(provider)
                print(state)
                params = dict(
                    appid=False,
                    # appid="wxfd382cba56728671",
                    response_type="code",
                    redirect_uri=return_url,
                    scope=provider['scope'],
                    # state=request.env['ir.config_parameter'].sudo().get_param('wechat_website_auth_state'),
                    state=json.dumps(state),
                    lang=request.env['ir.config_parameter'].sudo().get_param('wechat_website_auth_lang'),
                )
                # ----------------------------------------------------------------------
                # 请求CODE 的链接格式
                # https://open.weixin.qq.com/connect/qrconnect?appid=APPID&redirect_uri=REDIRECT_URI&response_type=code&scope=SCOPE&state=STATE#wechat_redirect
                # ----------------------------------------------------------------------
                provider['auth_link'] = "%s?%s%s" % (provider["auth_endpoint"],werkzeug.urls.url_encode(params),"#wechat_redirect")
                # print(provider)
                # print(provider['auth_link'])
        return providers

class OAuthController(http.Controller):
    @http.route("/wechat_auth_oauth", type="http", auth="none",)
    @fragment_to_query_string
    def wechat_website_authorize(self, **kw):
        code = kw.pop("code", None)
        state = json.loads(kw["state"])
        print(code,state)


    @http.route("/wechat_login_info", type="json", auth="none")
    def get_wechat_login_info(self, **kwargs):
        # TODO if "is_wechat_browser" in kwargs:
        data = {}
        companies = request.env["res.company"].search(  # type: ignore
            [(("allow_wechat_website_auth", "=", True))]
        )
        if len(companies) > 0:
            for company in companies:
                data["companies"].append(
                    {
                        "id": company["id"],
                        "name": company["abbreviated_name"],
                        "fullname": company["name"],
                        "shortname": company["shortname"],
                        "appid": company["wechat_website_auth_appid"],
                    }
                )
        data.update({
            "qrcode_display_method":request.env['ir.config_parameter'].sudo().get_param('wechat_website_auth_qrcode_display_method')
        })

        return data

