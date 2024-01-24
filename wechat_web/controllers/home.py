# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import requests

import odoo
import odoo.modules.registry
from odoo import api, http, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.service import security
from odoo.tools import ustr
from odoo.tools.translate import _
from odoo.addons.web.controllers.utils import (
    ensure_db,
    _get_login_redirect_url,
    is_user_internal,
)
import werkzeug.urls
import werkzeug.utils
from urllib.parse import urlparse, urlencode
from werkzeug.exceptions import BadRequest

_logger = logging.getLogger(__name__)


# Shared parameters for all login/signup flows
SIGN_UP_REQUEST_PARAMS = {
    "db",
    "login",
    "debug",
    "token",
    "message",
    "error",
    "scope",
    "mode",
    "redirect",
    "redirect_hostname",
    "email",
    "name",
    "partner_id",
    "password",
    "confirm_password",
    "city",
    "country_id",
    "lang",
    "signup_email",
}
LOGIN_SUCCESSFUL_PARAMS = set()


class WechatController(http.Controller):
    @http.route("/wechat", type="http", auth="none")
    def index(self, s_action=None, db=None, **kw):
        print("首页", request.db, request.session.uid)
        print("首页", kw)
        if (
            request.db
            and request.session.uid
            and not is_user_internal(request.session.uid)
        ):
            return request.redirect_query(
                "/wechat/web/login_successful", query=request.params
            )
        return request.redirect_query("/wechat/web", query=request.params)

    # ideally, this route should be `auth="user"` but that don't work in non-monodb mode.
    @http.route("/wechat/web", type="http", auth="none")
    def wechat_client(self, s_action=None, **kw):
        # 确保我们既有数据库又有用户
        ensure_db()
        print("web", request.db, request.session.uid, kw)
        if not request.session.uid:
            return request.redirect("/wechat/web/login", 303)
        if kw.get("redirect"):
            print("redirect", kw.get("redirect"))
            return request.redirect(kw.get("redirect"), 303)
        if not security.check_session(request.session, request.env):
            print("not security.check_session")
            raise http.SessionExpiredException("Session expired")
        if not is_user_internal(request.session.uid):
            print("not is_user_internal")
            pass
            # return request.redirect("/wechat/web/login_successful", 303)

        # Side-effect, 刷新会话生存期
        request.session.touch()

        # Restore the user on the environment, it was lost due to auth="none"
        # 在环境中恢复用户，由于 auth="none" 而丢失
        request.update_env(user=request.session.uid)
        try:
            context = request.env["ir.http"].webclient_rendering_context()
            response = request.render(
                "wechat_web.webclient_bootstrap", qcontext=context
            )
            response.headers["X-Frame-Options"] = "DENY"
            return response
        except AccessError:
            return request.redirect("/wechat/web/login?error=access")

    def _login_redirect(self, uid, redirect=None):
        return _get_login_redirect_url(uid, redirect)

    @http.route("/wechat/web/login", type="http", auth="none")
    def wechat_login(self, redirect=None, **kw):
        ensure_db()
        print(kw)
        request.params["login_success"] = False
        if request.httprequest.method == "GET" and redirect and request.session.uid:
            return request.redirect(redirect)

        # 模拟混合 auth=user/auth=public，尽管使用 auth=none 能够在未选择数据库时重定向用户 - cfr ensure_db（）
        if request.env.uid is None:
            if request.session.uid is None:
                # no user -> auth=public with specific website public user
                request.env["ir.http"]._auth_method_public()
            else:
                # auth=user
                request.update_env(user=request.session.uid)

        values = {
            k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS
        }
        try:
            values["databases"] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values["databases"] = None

        if request.httprequest.method == "POST":
            try:
                uid = request.session.authenticate(
                    request.db, request.params["login"], request.params["password"]
                )
                request.params["login_success"] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values["error"] = _("Wrong login/password")
                else:
                    values["error"] = e.args[0]
        else:
            if "error" in request.params and request.params.get("error") == "access":
                values["error"] = _(
                    "Only employees can access this database. Please contact the administrator."
                )
            elif "oauth_error" in request.params:
                error = request.params.get("oauth_error")
                print("微信验证错误2", error)
                if error:
                    error_code = (
                        request.env["wechat.error_codes"]
                        .sudo()
                        .search_read(
                            domain=[("code_text", "=", error)],
                            fields=["name"],
                        )
                    )
                    if error_code:
                        error = _("%s: %s") % (error, error_code[0]["name"])
                    else:
                        error = _("%s: %s") % (error, _("unknown error"))
                else:
                    error = None
                values["error"] = error

        if "login" not in values and request.session.get("auth_login"):
            values["login"] = request.session.get("auth_login")

        if not odoo.tools.config["list_db"]:
            values["disable_database_manager"] = True

        auth_link = self.generate_official_account_login_link()
        if not auth_link:
            values.update({"error": _("WeChat authentication is not activated!")})
        values.update({"auth_link": auth_link})
        response = request.render("wechat_web.login", values)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    @http.route(
        "/wechat/web/login_successful",
        type="http",
        auth="user",
        website=True,
        sitemap=False,
    )
    def wechat_login_successful_external_user(self, **kwargs):
        """Landing page after successful login for external users (unused when portal is installed)."""
        valid_values = {k: v for k, v in kwargs.items() if k in LOGIN_SUCCESSFUL_PARAMS}
        return request.render("wechat_web.login_successful", valid_values)

    @http.route(
        "/wechat/h5_auth",
        type="http",
        auth="none",
    )
    def wechat_h5_auth(self, **kw):
        print(kw)

        code = kw.pop("code", None)
        try:
            state = json.loads(kw["state"])
        except:
            state_str = kw["state"]
            if "\\" in state_str:
                state_str = state_str.replace("\\", "")
            state_array = state_str.replace("{", "").replace("}", "").split(",")
            state = {}
            for state_item in state_array:
                state_object = state_item.split(":")
                for index, s in enumerate(state_object):
                    if "'" in s:
                        state_object[index] = state_object[index].replace("'", "")

                if len(state_object) == 2:
                    state.update({state_object[0]: state_object[1]})
                elif len(state_object) == 3:
                    state.update(
                        {state_object[0]: state_object[1] + ":" + state_object[2]}
                    )
        print(state, type(state))
        ICP = request.env["ir.config_parameter"].sudo()
        wechat_app_id = ICP.get_param("wechat_official_accounts_app")
        app = (
            request.env["wechat.applications"]
            .sudo()
            .search_read([("id", "=", wechat_app_id)])[0]
        )
        lang = ICP.get_param("wechat_official_accounts_web_auth_lang")
        get_access_token_url = (
            "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code"
            % (app["appid"], app["secret"], code)
        )
        try:
            response = requests.get(get_access_token_url).json()
        except Exception as e:
            print(str(e))
        finally:
            if "errcode" in response:
                url = "/wechat/web/login?oauth_error=%s" % response["errcode"]
                return request.redirect(url)
            access_token = response["access_token"]
            openid = response["openid"]
            # 拉取用户信息(需scope为 snsapi_userinfo)
            get_userinfo_url = (
                "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=%s"
                % (access_token, openid, lang)
            )
            try:
                userinfo = requests.get(get_userinfo_url).json()
            except Exception as e:
                print(str(e))
            else:
                pass
            finally:
                if "errcode" in userinfo:
                    url = "/web/login?oauth_error=%s" % userinfo["errcode"]
                    return request.redirect(url)

                # 确保 request.session.db 和 state['d'] 相同，更新会话并重试请求
                dbname = state["d"]
                if not http.db_filter([dbname]):
                    return BadRequest()
                ensure_db(db=dbname)

                provider = state["p"]
                userinfo.update(
                    {
                        "access_token": response["access_token"],
                        "expires_in": response["expires_in"],
                        "refresh_token": response["refresh_token"],
                    }
                )
                try:
                    # auth_oauth可能会创建一个新用户，提交使下面的 authenticate() 自己的事务可见
                    db, login, key = (
                        request.env["res.users"]
                        .with_user(SUPERUSER_ID)
                        .wechat_auth_oauth(provider, userinfo)
                    )
                    request.env.cr.commit()

                    action = state.get("a")
                    menu = state.get("m")
                    redirect = state["r"] if state.get("r") else False
                    print(redirect)
                    url = "/web"
                    if redirect:
                        url = redirect
                    elif action:
                        url = "/web#action=%s" % action
                    elif menu:
                        url = "/web#menu_id=%s" % menu
                    print(url)
                    print(urlparse(url).path)
                    pre_uid = request.session.authenticate(db, login, key)  # type: ignore
                    resp = request.redirect(_get_login_redirect_url(pre_uid, url), 303)  # type: ignore
                    resp.autocorrect_location_header = False
                    resp.location = "/wechat/web?redirect=%s" % urlparse(url).path

                    return resp
                except AttributeError:
                    # auth_signup is not installed
                    url = "/wechat/web/login?oauth_error=1"
                except AccessDenied:
                    # oauth credentials not valid, user could be on a temporary session
                    url = "/wechat/web/login?oauth_error=3"
                except Exception as e:
                    # signup error
                    url = "/wechat/web/login?oauth_error=2"

    @http.route("/wechat/web/health", type="http", auth="none", save_session=False)
    def wechat_health(self):
        data = json.dumps(
            {
                "status": "pass",
            }
        )
        headers = [("Content-Type", "application/json"), ("Cache-Control", "no-store")]
        return request.make_response(data, headers)

    def generate_official_account_login_link(self):
        """
        生成公众号登录链接
        """
        return_url = request.httprequest.url_root + "wechat/h5_auth"

        providers = (
            request.env["auth.oauth.provider"]
            .sudo()
            .search_read(
                [
                    ("enabled", "=", True),
                    (
                        "auth_endpoint",
                        "=",
                        "https://open.weixin.qq.com/connect/oauth2/authorize",
                    ),
                ]
            )
        )
        provider = False
        if len(providers) > 0:
            provider = providers[0]
        else:
            return False
        state = self.get_state(provider)
        ICP = request.env["ir.config_parameter"].sudo()
        wechat_app_id = ICP.get_param("wechat_official_accounts_app")
        app = (
            request.env["wechat.applications"]
            .sudo()
            .search_read([("id", "=", wechat_app_id)])[0]
        )
        params = dict(
            appid=app["appid"],
            response_type="code",
            redirect_uri=return_url,
            scope="snsapi_userinfo",
            forcePopup=True,
            state=json.dumps(state).replace(" ", ""),
        )
        # -------------------------------------------------------
        # 请求CODE 的链接格式
        # "https://open.weixin.qq.com/connect/oauth2/authorize?appid=APPID&redirect_uri=REDIRECT_URI&response_type=code&scope=snsapi_userinfo&state=SCOPE#wechat_redirect"
        # -------------------------------------------------------
        auth_link = "%s?%s%s" % (
            "https://open.weixin.qq.com/connect/oauth2/authorize",
            werkzeug.urls.url_encode(params),
            "#wechat_redirect",
        )

        return auth_link

    def get_state(self, provider):
        redirect = request.params.get("redirect") or "wechat"
        if not redirect.startswith(("//", "http://", "https://")):
            redirect = "%s%s" % (
                request.httprequest.url_root,
                redirect[1:] if redirect[0] == "/" else redirect,
            )
        state = dict(
            d=request.session.db,
            p=provider["id"],
            r=werkzeug.urls.url_quote_plus(redirect),
        )
        token = request.params.get("token")
        if token:
            state["t"] = token
        return state
