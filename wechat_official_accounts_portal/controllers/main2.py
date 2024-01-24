# -*- coding: utf-8 -*-

import json
import logging
import odoo
import odoo.modules.registry
from odoo.exceptions import AccessError
from odoo.addons.wechat_base.controllers.woa import WeChatOfficialAccounts as WOA  # type: ignore
from odoo import http, models, fields, _
from odoo.http import request, Response
from odoo.service import security
from odoo.addons.web.controllers.utils import (
    ensure_db,
    _get_login_redirect_url,
    is_user_internal,
)
import werkzeug.urls
import werkzeug.utils
from werkzeug.exceptions import BadRequest

_logger = logging.getLogger(__name__)


# 所有登录/注册流程的共享参数
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


class WeChatOfficialAccountHome(WOA):
    """ """

    @http.route("/wechat", type="http", auth="none")
    def index(self, s_action=None, db=None, **kw):
        print("index", kw)
        if (
            request.db
            and request.session.uid
            and not is_user_internal(request.session.uid)
        ):
            return request.redirect_query(
                "/wechat/login_successful", query=request.params
            )
        return request.redirect_query("/wechat/web", query=request.params)

    @http.route("/wechat/web", type="http", auth="none")
    def web_client(self, s_action=None, **kw):
        # Ensure we have both a database and a user
        ensure_db()
        print("web_client", kw)
        if not request.session.uid:
            return request.redirect("/wechat/login", 303)
        if kw.get("redirect"):
            return request.redirect(kw.get("redirect"), 303)
        if not security.check_session(request.session, request.env):
            raise http.SessionExpiredException("Session expired")
        if not is_user_internal(request.session.uid):
            return request.redirect("/wechat/login_successful", 303)

        # Side-effect, refresh the session lifetime
        request.session.touch()

        # Restore the user on the environment, it was lost due to auth="none"
        request.update_env(user=request.session.uid)
        try:
            context = request.env["ir.http"].webclient_rendering_context()
            response = request.render(
                "wechat_official_accounts_portal.webclient_bootstrap", qcontext=context
            )
            response.headers["X-Frame-Options"] = "DENY"
            return response
        except AccessError:
            return request.redirect("/wechat/login?error=access")

    @http.route("/wechat/login", type="http", auth="none")
    def wechat_login(self, redirect=None, **kw):
        ensure_db()
        print("wechat_login", kw)
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

        if "login" not in values and request.session.get("auth_login"):
            values["login"] = request.session.get("auth_login")

        if not odoo.tools.config["list_db"]:
            values["disable_database_manager"] = True

        values.update({"auth_link": self.generate_official_account_login_link()})

        response = request.render("wechat_official_accounts_portal.login", values)

        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    def generate_official_account_login_link(self):
        """
        生成公众号登录链接
        """
        return_url = request.httprequest.url_root + "wechat"
        state = self.get_state()
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

    def get_state(self):
        redirect = request.params.get("redirect")
        # print(request.httprequest.url_root)
        # print(request.session.db)
        # if not redirect.startswith(("//", "http://", "https://")):
        #     redirect = "%s%s" % (
        #         request.httprequest.url_root,
        #         redirect[1:] if redirect[0] == "/" else redirect,
        #     )
        state = dict(
            d=request.session.db,
            r=werkzeug.urls.url_quote_plus(redirect),
        )
        token = request.params.get("token")
        if token:
            state["t"] = token
        return state
