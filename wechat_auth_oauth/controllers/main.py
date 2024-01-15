# -*- coding: utf-8 -*-

# !参考 \addons\auth_oauth\controllers\main.py
import time
import requests # type: ignore
import logging
import json
import werkzeug.urls # type: ignore
import werkzeug.utils # type: ignore
from urllib.parse import urlparse, urlencode
from werkzeug.exceptions import BadRequest # type: ignore

from odoo import api, http, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, ValidationError, UserError
from odoo.http import request, Response
from odoo import registry as registry_get
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home  # type: ignore
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string  # type: ignore
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url  # type: ignore
from odoo.addons.wechat_api.tools.security import WeChatApiToolsSecurity  # type: ignore

_logger = logging.getLogger(__name__)

WECHAT_BROWSER_MESSAGES = {
    "not_wechat_browser": _(
        "The current browser is not an Wechat built-in browser, so the one-click login function cannot be used."
    ),
    "is_wechat_browser": _(
        "It is detected that the page is opened in the built-in browser of Wechat."
    ),
}

class WeChatOAuthLogin(Home):

    def list_providers(self):
        try:
            providers = (
                request.env["auth.oauth.provider"]
                .sudo()
                .search_read([("enabled", "=", True)])
            )
        except Exception:
            providers = []
        for provider in providers:
            if (
                "https://open.weixin.qq.com/connect/qrconnect"
                in provider["auth_endpoint"]
            ):
                return_url = (
                    request.httprequest.url_root + "wechat_scan_register_or_login"
                )
                state = self.get_state(provider)
                ICP = request.env["ir.config_parameter"].sudo()
                appid = ICP.get_param("wechat_website_auth_appid")
                # state = ICP.get_param("wechat_website_auth_state")
                lang = ICP.get_param("wechat_website_auth_lang")
                params = dict(
                    appid=appid,
                    response_type="code",
                    redirect_uri=return_url,
                    scope=provider["scope"],
                    state=json.dumps(state).replace(" ", ""),
                    # state=state,
                    lang=lang,
                )

                # -------------------------------------------------------
                # 请求CODE 的链接格式
                # https://open.weixin.qq.com/connect/qrconnect?appid=APPID&redirect_uri=REDIRECT_URI&response_type=code&scope=SCOPE&state=STATE#wechat_redirect
                # -------------------------------------------------------
                provider["auth_link"] = "%s?%s%s" % (
                    provider["auth_endpoint"],
                    werkzeug.urls.url_encode(params),
                    "#wechat_redirect",
                )

            elif (
                "https://open.weixin.qq.com/connect/oauth2/authorize"
                in provider["auth_endpoint"]
            ):
                return_url = (
                    request.httprequest.url_root + "wechat_one_click_register_or_login"
                )
                state = self.get_state(provider)
                ICP = request.env["ir.config_parameter"].sudo()
                appid = ICP.get_param("wechat_official_accounts_developer_appid")
                params = dict(
                    appid=appid,
                    response_type="code",
                    redirect_uri=return_url,
                    scope=provider["scope"],
                    forcePopup=True,
                    state=json.dumps(state).replace(" ", ""),
                )
                # -------------------------------------------------------
                # 请求CODE 的链接格式
                # "https://open.weixin.qq.com/connect/oauth2/authorize?appid=APPID&redirect_uri=REDIRECT_URI&response_type=code&scope=snsapi_userinfo&state=SCOPE#wechat_redirect"
                # -------------------------------------------------------

                provider["auth_link"] = "%s?%s%s" % (
                    provider["auth_endpoint"],
                    werkzeug.urls.url_encode(params),
                    "#wechat_redirect",
                )

        return providers

    @http.route()
    def web_login(self, *args, **kw):
        response = super(WeChatOAuthLogin, self).web_login(*args, **kw)
        if response.is_qweb:
            error = request.params.get('oauth_error')
            print(error,type(error))
            if error =="10003":
                error = _("%s:redirect_uri domain name is inconsistent with the background configuration") % error
            elif error =="10004":
                error = _("%s:This official account is banned") % error
            elif error =="10005":
                error = _("%s:This official account does not have the permission of these scopes") % error
            elif error =="10006":
                error = _("%s:You must pay attention to this test official account") % error
            elif error =="10009":
                error = _("%s:It's too frequent, please try again later") % error
            elif error =="10010":
                error = _("%s:The scope cannot be empty") % error
            elif error =="10011":
                error = _("%s:redirect_uri can't be empty") % error
            elif error =="10012":
                error = _("%s:The appid cannot be empty") % error
            elif error =="10013":
                error = _("%s:state cannot be empty") % error
            elif error =="10015":
                error = _("%s:The Official Account does not authorize a third-party platform, please check the authorization status") % error
            elif error == '10016':
                error = _("%s:The Appid of the WeChat Open Platform is not supported, please use the Official Account Appid") % error
            elif error == '40125':
                error = _("%s:Invalid WeChat Secret, please contact the administrator.") % error
            elif error == '40163':
                error = _("%s:Code been used, please contact the administrator.") % error
            elif error !="":
                error = _("%s:Unknown error code") % error
            else:
                error = None

            if error:
                response.qcontext['error'] = error
        return response

    @http.route('/wechat_reset_login_name', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_login_name(self, *args, **kw):
        """
        重置用户名
        """
        print(args,kw)
        # qcontext = self.get_auth_signup_qcontext()
        # print(qcontext)

        response = request.render('wechat_auth_oauth.reset_login_name', {})
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

class OAuthController(http.Controller):

    @http.route(
        "/wechat_scan_register_or_login",
        type="http",
        auth="none",
    )
    @fragment_to_query_string
    def wechat_scan_register_or_login(self, **kw):
        """
        通过微信扫码注册或登录
        """
        code = kw.pop("code", None)
        state_str = kw["state"]
        if "\\" in state_str:
            state_str = state_str.replace("\\", "")
        state_array = state_str.replace("{", "").replace("}", "").split(",")
        state = {}
        for state_item in state_array:
            state_object = state_item.split(":")
            if len(state_object) == 2:
                state.update({state_object[0]: state_object[1]})
            elif len(state_object) == 3:
                state.update({state_object[0]: state_object[1] + ":" + state_object[2]})


        ICP = request.env["ir.config_parameter"].sudo()
        appid = ICP.get_param("wechat_website_auth_appid")
        secret = ICP.get_param("wechat_website_auth_secret")
        get_access_token_url = (
            "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code"
            % (appid, secret, code)
        )
        try:
            response = requests.get(get_access_token_url).json()
        except Exception as e:
            print(str(e))
        finally:
            print(response)
            if "errcode" in response:
                url = "/web/login?oauth_error=%s" % response["errcode"]
                return request.redirect(url)

            current_time = time.time()  # 当前时间戳
            access_token = response["access_token"]
            expires_in = response["expires_in"]
            refresh_token = response["refresh_token"]
            openid = response["openid"]
            scope = response["scope"]
            unionid = response["unionid"]

            # 通过 access_token 拉取用户信息
            if access_token:
                get_userinfo_url = (
                    "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s"
                    % (access_token, openid)
                )
                try:
                    userinfo = requests.get(get_userinfo_url).json()
                except Exception as e:
                    print(str(e))
                finally:
                    # 确保 request.session.db 和 state['d'] 相同，更新会话并重试请求
                    dbname = state["d"]
                    if not http.db_filter([dbname]):
                        return BadRequest()
                    ensure_db(db=dbname)

                    provider = state["p"]
                    userinfo.update({
                        "access_token":response["access_token"],
                        "expires_in":response["expires_in"],
                        "refresh_token":response["refresh_token"],
                    })
                    try:
                        # auth_oauth可能会创建一个新用户，提交使下面的 authenticate() 自己的事务可见
                        db, login, key = request.env['res.users'].with_user(SUPERUSER_ID).wechat_auth_oauth(provider, userinfo)
                        request.env.cr.commit()

                        action = state.get("a")
                        menu = state.get("m")
                        redirect = state["r"] if state.get("r") else False

                        url = "/web"
                        if redirect:
                            url = redirect
                        elif action:
                            url = "/web#action=%s" % action
                        elif menu:
                            url = "/web#menu_id=%s" % menu

                        pre_uid = request.session.authenticate(db, login, key)  # type: ignore
                        resp = request.redirect(_get_login_redirect_url(pre_uid, url), 303)  # type: ignore
                        resp.autocorrect_location_header = False

                        # 由于/web是硬编码的，请验证用户是否有权登录
                        if request.env.user.login == request.env.user.wechat_openid or request.env.user.login == request.env.user.wechat_unionid:
                            # 需要重置用户名
                            resp.location = "/wechat_reset_login_name"
                            if request.env.user._is_internal():
                                resp.location = '/wechat_reset_login_name?redirect_uri=web'
                            else:
                                resp.location = '/wechat_reset_login_name?redirect_uri=my'
                        else:
                            if request.env.user._is_internal():
                                resp.location = '/web'
                            else:
                                resp.location = '/my'
                        return resp
                    except AttributeError:
                        # auth_signup is not installed
                        url = "/web/login?oauth_error=1"
                    except AccessDenied:
                        # oauth credentials not valid, user could be on a temporary session
                        url = "/web/login?oauth_error=3"
                    except Exception as e:
                        # signup error
                        url = "/web/login?oauth_error=2"


    @http.route(
        "/wechat_one_click_register_or_login",
        type="http",
        auth="none",
    )
    @fragment_to_query_string
    def wechat_one_click_register_or_login(self,**kw):
        """
        微信内置浏览器一键注册和登录
        """
        # 通过code换取网页授权access_token
        code = kw.pop("code", None)

        print(kw["state"],type(kw["state"]))
        # 微信开者工具和手机首位生成的 state 值 不一致，故需要进行 try except 进行处理
        # {d:wechat,p:13,r:https://genealogy.odooeasy.cn/web} <class 'str'>  微信开发者工具的值
        # {"d":"wechat","p":13,"r":"https%3A%2F%2Fgenealogy.odooeasy.cn%2Fweb"} <class 'str'> 手机微信的值
        try:
            print("--------1",kw['state'],type(kw['state']))
            state = json.loads(kw['state'])
        except:
            print("--------2",kw['state'],type(kw['state']))
            state_str = kw["state"]
            if "\\" in state_str:
                state_str = state_str.replace("\\", "")
            state_array = state_str.replace("{", "").replace("}", "").split(",")
            state = {}
            for state_item in state_array:
                state_object = state_item.split(":")
                print(state_object,type(state_object))
                for index, s in enumerate(state_object):
                    if "'" in s:
                        state_object[index] = state_object[index].replace("'", "")

                if len(state_object) == 2:
                    state.update({state_object[0]: state_object[1]})
                elif len(state_object) == 3:
                    state.update({state_object[0]: state_object[1] + ":" + state_object[2]})

        print("--------3",state,type(state))
        ICP = request.env["ir.config_parameter"].sudo()
        appid = ICP.get_param("wechat_official_accounts_developer_appid")
        secret = ICP.get_param("wechat_official_accounts_developer_secret")
        lang  = ICP.get_param("wechat_official_accounts_web_auth_lang")
        get_access_token_url = (
            "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code"
            % (appid, secret, code)
        )
        try:
            response = requests.get(get_access_token_url).json()
        except Exception as e:
            print(str(e))
        finally:
            # {'access_token': '', 'expires_in': 7200, 'refresh_token': '', 'openid': '', 'scope': ''}
            current_time = time.time()  # 当前时间戳
            access_token = response["access_token"]
            expires_in = response["expires_in"]
            refresh_token = response["refresh_token"]
            openid = response["openid"]
            scope = response["scope"]

            # 拉取用户信息(需scope为 snsapi_userinfo)
            get_userinfo_url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=%s" % (access_token, openid, lang)
            try:
                userinfo = requests.get(get_userinfo_url).json()
            except Exception as e:
                print(str(e))
            finally:
                # 确保 request.session.db 和 state['d'] 相同，更新会话并重试请求
                # print(state,type(state))
                dbname = state["d"]
                if not http.db_filter([dbname]):
                    return BadRequest()
                ensure_db(db=dbname)

                provider = state["p"]
                userinfo.update({
                    "access_token":response["access_token"],
                    "expires_in":response["expires_in"],
                    "refresh_token":response["refresh_token"],
                })
                try:
                    # auth_oauth可能会创建一个新用户，提交使下面的 authenticate() 自己的事务可见
                    db, login, key = request.env['res.users'].with_user(SUPERUSER_ID).wechat_auth_oauth(provider, userinfo)
                    request.env.cr.commit()

                    action = state.get("a")
                    menu = state.get("m")
                    print(state["r"])
                    redirect = state["r"] if state.get("r") else False

                    url = "/web"
                    if redirect:
                        url = redirect
                    elif action:
                        url = "/web#action=%s" % action
                    elif menu:
                        url = "/web#menu_id=%s" % menu

                    pre_uid = request.session.authenticate(db, login, key)  # type: ignore
                    resp = request.redirect(_get_login_redirect_url(pre_uid, url), 303)  # type: ignore
                    resp.autocorrect_location_header = False

                    # 由于/web是硬编码的，请验证用户是否有权登录
                    if request.env.user.login == request.env.user.wechat_openid or request.env.user.login == request.env.user.wechat_unionid:
                        # 需要重置用户名
                        resp.location = "/wechat_reset_login_name"
                        if request.env.user._is_internal():
                            resp.location = '/wechat_reset_login_name?redirect_uri=web'
                        else:
                            resp.location = '/wechat_reset_login_name?redirect_uri=my'
                    else:
                        if request.env.user._is_internal():
                            resp.location = '/web'
                        else:
                            resp.location = '/my'
                    return resp

                    return resp
                except AttributeError:
                    # auth_signup is not installed
                    url = "/web/login?oauth_error=1"
                except AccessDenied:
                    # oauth credentials not valid, user could be on a temporary session
                    url = "/web/login?oauth_error=3"
                except Exception as e:
                    # signup error
                    url = "/web/login?oauth_error=2"

    @http.route("/get_provider_wechat", type="json", auth="none")
    def get_provider_wechat(self, **kwargs):
        # TODO if "is_wechat_browser" in kwargs:
        data = {}

        return_url = request.httprequest.url_root + "wechat_scan_register_or_login"
        css_url = (
            request.httprequest.url_root
            + "wechat_auth_oauth/static/str/legacy/public/css/wehcat_qrcode.css"
        )
        providers = (
            request.env["auth.oauth.provider"]
            .sudo()
            .search_read([("enabled", "=", True)])
        )

        ICP = request.env["ir.config_parameter"].sudo()
        if len(providers) == 0:
            return False
        for provider in providers:
            if (
                "https://open.weixin.qq.com/connect/qrconnect"
                in provider["auth_endpoint"]
            ):
                # 判断是微信网站登录
                appid = ICP.get_param("wechat_website_auth_appid")
                qrcode_display_method = ICP.get_param(
                    "wechat_website_auth_qrcode_display_method"
                )
                # state = ICP.get_param("wechat_website_auth_state")
                data.update(
                    {
                        "qrcode_display_method": qrcode_display_method,
                        "appid": appid,
                        "scope": "snsapi_login",
                        "redirect_uri": return_url,
                        "state": json.dumps(self.get_state()),
                        # "state": state,
                        "style": "black",
                        "href": css_url,
                    }
                )

        return data

    def get_state(self):
        provider_wechat = False
        try:
            providers = (
                request.env["auth.oauth.provider"]
                .sudo()
                .search_read([("enabled", "=", True)])
            )
        except Exception:
            providers = []
        for provider in providers:
            if (
                "https://open.weixin.qq.com/connect/qrconnect"
                in provider["auth_endpoint"]
            ):
                provider_wechat = provider
        if provider_wechat:
            redirect = request.params.get("redirect") or "web"
            if not redirect.startswith(("//", "http://", "https://")):
                redirect = "%s%s" % (
                    request.httprequest.url_root,
                    redirect[1:] if redirect[0] == "/" else redirect,
                )
            state = dict(
                d=request.session.db,
                p=provider_wechat["id"],
                r=redirect,
                # r=werkzeug.urls.url_quote_plus(redirect),
            )
            token = request.params.get("token")
            if token:
                state["t"] = token
            state = json.dumps(state).replace(" ", "")
            return state
        else:
            return False
