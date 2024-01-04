# -*- coding: utf-8 -*-

# !参考 \addons\auth_oauth\controllers\main.py
import requests
import logging
import json
import werkzeug.urls
import werkzeug.utils
from urllib.parse import urlparse
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

                return_url = request.httprequest.url_root + 'wechat_scan_code_auth_oauth'
                # state = self.get_state(provider)

                ICP = request.env['ir.config_parameter'].sudo()
                appid= ICP.get_param('wechat_website_auth_appid')
                state = ICP.get_param('wechat_website_auth_state')
                lang= ICP.get_param('wechat_website_auth_lang')
                params = dict(
                    appid=appid,
                    response_type="code",
                    redirect_uri=return_url,
                    scope=provider['scope'],
                    # state=json.dumps(state, ensure_ascii=False, indent=4).encode('utf-8'),
                    state=state,
                    lang=lang,
                )
                # ----------------------------------------------------------------------
                # 请求CODE 的链接格式
                # https://open.weixin.qq.com/connect/qrconnect?appid=APPID&redirect_uri=REDIRECT_URI&response_type=code&scope=SCOPE&state=STATE#wechat_redirect
                # ----------------------------------------------------------------------
                provider['auth_link'] = "%s?%s%s" % (provider["auth_endpoint"],werkzeug.urls.url_encode(params),"#wechat_redirect")
                # print(provider['auth_link'])
        return providers

class OAuthController(http.Controller):
    @http.route("/wechat_scan_code_auth_oauth", type="http", auth="none",)
    @fragment_to_query_string
    def wechat_website_authorize(self, **kw):
        code = kw.pop("code", None)
        state = kw.pop("state", None)
        # TODO 待验证 state
        # 参考文档 https://www.cnblogs.com/mayanan/p/16177596.html

        ICP = request.env['ir.config_parameter'].sudo()
        appid = ICP.get_param('wechat_website_auth_appid')
        secret = ICP.get_param('wechat_website_auth_secret')
        api_url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (appid,secret,code)
        print(api_url)
        try:
            response = requests.get(api_url).json()
        except Exception as e:
            print(str(e))
        finally:
            # {'access_token': '76_m0rO2g3nm53SBINskXRD4diQyuVgkATexDme3dAoTzhKSnfGAlt6IaYrTiwlwcfNMuPFilkQ7kjw8R4r22gu__TVRTpJ100M0SE9VQn1Ojw', 'expires_in': 7200, 'refresh_token': '76_nJoO-eipbCsbtokIQ4R9VxsXRwdRajhjKfZe750SAGfbzUzfAANoKPC1s6ARrRwihqRzKV4Lc5HCMefeQ3LxGPR7YpXiKzcfLIZxHPrtDQA', 'openid': 'oNaRq69tMYE3TUbURk9SpA6qGPSI', 'scope': 'snsapi_login', 'unionid': 'oN6TO6UDTTSDl_i147wc671KB-po'}
            print(response)
            # print(response["access_token"])
            # print(response["expires_in"])
            # print(response["refresh_token"])
            # print(response["openid"])
            # print(response["scope"])
            # print(response["unionid"])
            print("---------------")


    @http.route("/get_provider_wechat", type="json", auth="none")
    def get_provider_wechat(self, **kwargs):
        # TODO if "is_wechat_browser" in kwargs:
        data = {}

        return_url = request.httprequest.url_root + 'wechat_scan_code_auth_oauth'
        css_url = request.httprequest.url_root + 'wechat_auth_oauth/static/str/legacy/public/css/wehcat_qrcode.css'
        providers = request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])

        ICP = request.env['ir.config_parameter'].sudo()
        if len(providers) ==0:
            return False
        for provider in providers:
            if "https://open.weixin.qq.com/connect/qrconnect" in provider["auth_endpoint"]:
                # 判断是微信网站登录
                appid = ICP.get_param('wechat_website_auth_appid')
                qrcode_display_method = ICP.get_param('wechat_website_auth_qrcode_display_method')
                state = ICP.get_param('wechat_website_auth_state')
                data.update(
                    {
                        "qrcode_display_method":qrcode_display_method,
                        "appid": appid,
                        "scope": "snsapi_login",
                        "redirect_uri": return_url,

                        # "state":json.dumps(self.get_state(),ensure_ascii=False, indent=4).encode('utf-8'),
                        "state":state,
                        "style":"black",
                        "href":css_url,
                    }
                )

        return data

    def get_state(self):
        provider_wechat = False
        try:
            providers = request.env['auth.oauth.provider'].sudo().search_read([('enabled', '=', True)])
        except Exception:
            providers = []
        for provider in providers:
            if "https://open.weixin.qq.com/connect/qrconnect" in provider["auth_endpoint"]:
                provider_wechat = provider
        if provider_wechat:
            redirect = request.params.get('redirect') or 'web'
            if not redirect.startswith(('//', 'http://', 'https://')):
                redirect = '%s%s' % (request.httprequest.url_root, redirect[1:] if redirect[0] == '/' else redirect)
            state = dict(
                d=request.session.db,
                p=provider_wechat['id'],
                r=werkzeug.urls.url_quote_plus(redirect),
            )
            token = request.params.get('token')
            if token:
                state['t'] = token
            return state
        else:
            return False