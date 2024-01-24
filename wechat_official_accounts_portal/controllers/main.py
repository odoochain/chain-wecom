# -*- coding: utf-8 -*-

import time
import requests  # type: ignore
import logging
import json
import werkzeug.urls  # type: ignore
import werkzeug.utils  # type: ignore
from urllib.parse import urlparse, urlencode
from werkzeug.exceptions import BadRequest  # type: ignore

from odoo import api, http, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, ValidationError, UserError
from odoo.http import request, Response
from odoo import registry as registry_get
from odoo.addons.wechat_auth_oauth.controllers.main import WeChatOAuthLogin as Login  # type: ignore
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string  # type: ignore
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url  # type: ignore
from odoo.addons.wechat_api.tools.security import WeChatApiToolsSecurity  # type: ignore

_logger = logging.getLogger(__name__)


class WeChatOAuthLogin(Login):
    @http.route()
    def web_login(self, *args, **kw):
        response = super(WeChatOAuthLogin, self).web_login(*args, **kw)

        # 判断是微信公众号页面
        is_wechat_official_accounts_portal = False
        if "redirect" in kw and kw.get("redirect") and kw.get("redirect") == "wechat":
            is_wechat_official_accounts_portal = True

        # 验证链接
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
        if len(providers) > 0:
            provider = providers[0]
            is_wechat_official_accounts_portal = True

            return_url = (
                request.httprequest.url_root + "wechat/one_click_register_or_login"
            )
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
                scope=provider["scope"],
                forcePopup=True,
                state=json.dumps(state).replace(" ", ""),
            )
            auth_link = "%s?%s%s" % (
                provider["auth_endpoint"],
                werkzeug.urls.url_encode(params),
                "#wechat_redirect",
            )
            response.qcontext["auth_link"] = auth_link
        else:
            is_wechat_official_accounts_portal = False

        response.qcontext[
            "is_wechat_official_accounts_portal"
        ] = is_wechat_official_accounts_portal
        return response
