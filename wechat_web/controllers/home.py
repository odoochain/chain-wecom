# -*- coding: utf-8 -*-

import base64
import json
import math
import re

from werkzeug import urls

from odoo import http, tools, _, SUPERUSER_ID
from odoo.exceptions import (
    AccessDenied,
    AccessError,
    MissingError,
    UserError,
    ValidationError,
)
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq


class WechatPortal(Controller):
    MANDATORY_BILLING_FIELDS = [
        "name",
        "phone",
        "email",
        "street",
        "city",
        "country_id",
    ]
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name"]

    _items_per_page = 80

    def _prepare_portal_layout_values(self):
        """
        /wechat/web/home* 模板呈现的值。
        不包括记录计数。
        """
        # get customer sales rep
        sales_user_sudo = request.env["res.users"]
        partner_sudo = request.env.user.partner_id
        if partner_sudo.user_id and not partner_sudo.user_id._is_public():
            sales_user_sudo = partner_sudo.user_id

        return {
            "sales_user": sales_user_sudo,
            "page_name": "home",
        }

    def _prepare_home_portal_values(self, counters):
        """
        /wechat/web/home  路由模板呈现的值

        包括所显示徽章的记录计数。
        其中 'counters' 是显示的徽章列表，因此是要计算的列表。
        """
        return {}

    @route(["/wechat/web/counters"], type="json", auth="user", website=True)
    def counters(self, counters, **kw):
        return self._prepare_home_portal_values(counters)

    @route("/wechat/web/home", type="http", auth="user", website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        return request.render("wechat_web.home", values)

    @route("/wechat/web/my", type="http", auth="user", website=True)
    def my(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update(
            {
                "error": {},
                "error_message": [],
            }
        )

        if post and request.httprequest.method == "POST":
            error, error_message = self.details_form_validate(post)
            values.update({"error": error, "error_message": error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update(
                    {
                        key: post[key]
                        for key in self.OPTIONAL_BILLING_FIELDS
                        if key in post
                    }
                )
                for field in set(["country_id", "state_id"]) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({"zip": values.pop("zipcode", "")})
                self.on_account_update(values, partner)
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect("/wechat/web/home")

        countries = request.env["res.country"].sudo().search([])
        states = request.env["res.country.state"].sudo().search([])

        values.update(
            {
                "partner": partner,
                "countries": countries,
                "states": states,
                "has_check_vat": hasattr(request.env["res.partner"], "check_vat"),
                "partner_can_edit_vat": partner.can_edit_vat(),
                "redirect": redirect,
                "page_name": "my_account",
            }
        )
        print("my", values["page_name"])
        response = request.render("wechat_web.my", values)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    @route(["/wechat/web/my/account"], type="http", auth="user", website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update(
            {
                "error": {},
                "error_message": [],
            }
        )

        if post and request.httprequest.method == "POST":
            error, error_message = self.details_form_validate(post)
            values.update({"error": error, "error_message": error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update(
                    {
                        key: post[key]
                        for key in self.OPTIONAL_BILLING_FIELDS
                        if key in post
                    }
                )
                for field in set(["country_id", "state_id"]) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({"zip": values.pop("zipcode", "")})
                self.on_account_update(values, partner)
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect("/wechat/web/home")

        countries = request.env["res.country"].sudo().search([])
        states = request.env["res.country.state"].sudo().search([])

        values.update(
            {
                "partner": partner,
                "countries": countries,
                "states": states,
                "has_check_vat": hasattr(request.env["res.partner"], "check_vat"),
                "partner_can_edit_vat": partner.can_edit_vat(),
                "redirect": redirect,
                "page_name": "my_details",
            }
        )

        response = request.render("wechat_web.portal_my_details", values)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
        return response

    def on_account_update(self, values, partner):
        pass

    @route(
        "/wechat/web/my/security",
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def security(self, **post):
        values = self._prepare_portal_layout_values()
        values["get_error"] = get_error
        values["allow_api_keys"] = bool(
            request.env["ir.config_parameter"].sudo().get_param("portal.allow_api_keys")
        )
        values["open_deactivate_modal"] = False

        if request.httprequest.method == "POST":
            values.update(
                self._update_password(
                    post["old"].strip(), post["new1"].strip(), post["new2"].strip()
                )
            )

        return request.render(
            "wechat_web.portal_my_security",
            values,
            headers={
                "X-Frame-Options": "SAMEORIGIN",
                "Content-Security-Policy": "frame-ancestors 'self'",
            },
        )

    def _update_password(self, old, new1, new2):
        for k, v in [("old", old), ("new1", new1), ("new2", new2)]:
            if not v:
                return {
                    "errors": {
                        "password": {k: _("You cannot leave any password empty.")}
                    }
                }

        if new1 != new2:
            return {
                "errors": {
                    "password": {
                        "new2": _(
                            "The new password and its confirmation must be identical."
                        )
                    }
                }
            }

        try:
            request.env["res.users"].change_password(old, new1)
        except AccessDenied as e:
            msg = e.args[0]
            if msg == AccessDenied().args[0]:
                msg = _(
                    "The old password you provided is incorrect, your password was not changed."
                )
            return {"errors": {"password": {"old": msg}}}
        except UserError as e:
            return {"errors": {"password": e.name}}

        # update session token so the user does not get logged out (cache cleared by passwd change)
        # 更新会话令牌，以便用户不会注销（缓存通过 passwd 更改清除）
        new_token = request.env.user._compute_session_token(request.session.sid)
        request.session.session_token = new_token

        return {"success": {"password": True}}

    def details_form_validate(self, data, partner_creation=False):
        error = dict()
        error_message = []

        # 验证
        for field_name in self.MANDATORY_BILLING_FIELDS:
            if not data.get(field_name):
                error[field_name] = "missing"

        # 电子邮件验证
        if data.get("email") and not tools.single_email_re.match(data.get("email")):
            error["email"] = "error"
            error_message.append(
                _("Invalid Email! Please enter a valid email address.")
            )

        # 增值税验证
        partner = request.env.user.partner_id
        if data.get("vat") and partner and partner.vat != data.get("vat"):
            # 如果也是公共用户，请检查增值税。
            if partner_creation or partner.can_edit_vat():
                if hasattr(partner, "check_vat"):
                    if data.get("country_id"):
                        data["vat"] = request.env["res.partner"].fix_eu_vat_number(
                            int(data.get("country_id")), data.get("vat")
                        )
                    partner_dummy = partner.new(
                        {
                            "vat": data["vat"],
                            "country_id": (
                                int(data["country_id"])
                                if data.get("country_id")
                                else False
                            ),
                        }
                    )
                    try:
                        partner_dummy.check_vat()
                    except ValidationError as e:
                        error["vat"] = "error"
                        error_message.append(e.args[0])
            else:
                error_message.append(
                    _(
                        "Changing VAT number is not allowed once document(s) have been issued for your account. Please contact us directly for this operation."
                    )
                )

        # 必填字段为空的错误消息
        if [err for err in error.values() if err == "missing"]:
            error_message.append(_("Some required fields are empty."))

        unknown = [
            k
            for k in data
            if k not in self.MANDATORY_BILLING_FIELDS + self.OPTIONAL_BILLING_FIELDS
        ]
        if unknown:
            error["common"] = "Unknown field"
            error_message.append("Unknown field '%s'" % ",".join(unknown))

        return error, error_message


def get_error(e, path=""):
    """Recursively dereferences `path` (a period-separated sequence of dict
    keys) in `e` (an error dict or value), returns the final resolution IIF it's
    an str, otherwise returns None
    递归取消引用“e”（错误字典或值）中的“path”（以句点分隔的字典键序列），返回最终分辨率 IIF 它是一个 str，否则返回 None
    """
    for k in path.split(".") if path else []:
        if not isinstance(e, dict):
            return None
        e = e.get(k)

    return e if isinstance(e, str) else None
