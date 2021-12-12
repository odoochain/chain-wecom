# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.api import model_create_single


class WeComApps(models.Model):
    _name = "wecom.apps"
    _description = "Wecom Application"
    _order = "sequence"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        domain="[('is_wecom_organization', '=', True)]",
        copy=False,
        store=True,
    )

    code = fields.Char(
        string="Application Code",
        copy=True,
        help="Used to apply callback service and generate application parameters.",
    )  # 1.回调服务地址代码，便于在路由中查找 2.生成应用参数

    type = fields.Selection(
        [
            ("manage", "Manage Tools"),
            ("base", "Base application"),
            ("self", "Self built application"),
            ("third", "Third party application"),
        ],
        string="Application type",
        required=True,
        copy=True,
    )

    name = fields.Char(
        string="Name", copy=False, compute="_compute_name", store=True, index=True,
    )  # 企业应用名称
    app_name = fields.Char(
        string="Application Name", translate=True, copy=True,
    )  # 应用名称
    # display_name = fields.Char(compute="_compute_display_name", store=True, index=True)
    agentid = fields.Integer(string="Agent ID", copy=False)  # 企业应用id
    secret = fields.Char("Secret", default="", copy=False)
    square_logo_url = fields.Char(string="Square Logo", copy=False)  # 企业应用方形头像
    description = fields.Text(
        string="Description", translate=True, copy=False
    )  # 企业应用详情
    allow_userinfos = fields.Char(
        string="Visible range (personnel)", copy=False
    )  # 企业应用可见范围（人员），其中包括userid
    allow_partys = fields.Char(
        string="Visible range (Department)", copy=False
    )  # 企业应用可见范围（部门）
    allow_tags = fields.Char(string="Visible range (Tag))", copy=False)  # 企业应用可见范围（标签）
    close = fields.Boolean(string="Disabled", copy=False)  # 	企业应用是否被停用
    redirect_domain = fields.Char(string="Trusted domain name", copy=True)  # 企业应用可信域名
    report_location_flag = fields.Boolean(
        string="Open the geographic location and report", copy=False
    )  # 企业应用是否打开地理位置上报 0：不上报；1：进入会话上报；
    isreportenter = fields.Boolean(
        string="Report user entry event", copy=False
    )  # 企业应用是否打开进入会话上报 0：不上报；1：进入会话上报；
    home_url = fields.Char(string="Home page", copy=True)  # 企业应用主页url

    sequence = fields.Integer(default=0, copy=True)

    # 访问令牌
    access_token = fields.Char(string="Access Token", readonly=True, copy=False)
    expiration_time = fields.Datetime(
        string="Expiration Time", readonly=True, copy=False
    )

    _sql_constraints = [
        (
            "company_id_key_uniq",
            "unique (company_id,app_name)",
            _("The application name of each company must be unique !"),
        )
    ]

    @api.depends("company_id", "app_name", "type")
    def _compute_name(self):
        for app in self:
            labels = dict(self.fields_get(allfields=["type"])["type"]["selection"])[
                app.type
            ]
            if app.company_id:
                app.name = "%s/%s/%s" % (
                    app.company_id.abbreviated_name,
                    labels,
                    app.app_name,
                )
            else:
                app.name = "%s/%s" % (labels, app.app_name)

    def _default_callback_url(self):
        """
        默认回调地址
        :return:"""
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")
        if self.company_id and self.code:
            return base_url + "/wecom_callback/%s/%s" % (self.code, self.company_id.id,)
        else:
            return ""

    # 接收事件服务器配置
    # https://work.weixin.qq.com/api/doc/90000/90135/90930

    callback_url = fields.Char(
        string="Callback URL",
        store=True,
        readonly=True,
        default=_default_callback_url,
        copy=False,
    )  # 回调服务地址
    callback_url_token = fields.Char(
        string="Callback URL Token", copy=False
    )  # Token用于计算签名
    callback_aeskey = fields.Char(string="Callback AES Key", copy=False)  # 用于消息内容加密

    _sql_constraints = [
        (
            "code_company_uniq",
            "unique (code, company_id)",
            "The callback service name of each company is unique!",
        ),
    ]

    @api.onchange("company_id", "code")
    def _onchange_callback_url(self):
        """
        当公司和服务名称发生变化时，更新回调服务地址
        :return:
        """
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")

        if self.company_id and self.code:
            self.callback_url = base_url + "/wecom_callback/%s/%s" % (
                self.code,
                self.company_id.id,
            )
        else:
            self.callback_url = ""

    def get_app_info(self):
        """
        获取企业应用信息
        :param agentid:
        :return:
        """
        try:
            wecomapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.secret
            )
            response = wecomapi.httpCall(
                self.env["wecom.service_api_list"].get_server_api_call("AGENT_GET"),
                {"agentid": str(self.agentid)},
            )
        except ApiException as e:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                e, raise_exception=True
            )
        else:
            if response["errcode"] == 0:
                self.write(
                    {
                        "name": response["name"],
                        "square_logo_url": response["square_logo_url"],
                        "description": response["description"],
                        "allow_userinfos": response["allow_userinfos"]
                        if "allow_userinfos" in response
                        else "{}",
                        "allow_partys": response["allow_partys"]
                        if "allow_partys" in response
                        else "{}",
                        "allow_tags": response["allow_tags"]
                        if "allow_tags" in response
                        else "{}",
                        "close": response["close"],
                        "redirect_domain": response["redirect_domain"],
                        "report_location_flag": response["report_location_flag"],
                        "isreportenter": response["isreportenter"],
                        "home_url": response["home_url"],
                    }
                )
                msg = {
                    "title": _("Tips"),
                    "message": _("Successfully obtained application information!"),
                    "sticky": False,
                }
                return self.env["wecomapi.tools.action"].ApiSuccessNotification(msg)

    def set_app_info(self):
        """
        设置企业应用信息
        :param agentid:
        :return:
        """

    def get_access_token(self):
        """获取企业应用接口调用凭据（令牌）
        :return:
        """
        try:
            wecomapi = self.env["wecom.service_api"].InitServiceApi(
                self.company_id.corpid, self.secret
            )

        except ApiException as ex:
            return self.env["wecomapi.tools.action"].ApiExceptionDialog(
                ex, raise_exception=True
            )
        else:
            for res in self:
                if res.access_token is False:
                    # 令牌为空，则获取
                    res.write(
                        {
                            "access_token": wecomapi.access_token,
                            "expiration_time": wecomapi.expiration_time,
                        }
                    )
                    msg = {
                        "title": _("Tips"),
                        "message": _("The access token was successfully obtained!"),
                        "sticky": False,
                    }
                    # return self.env["wecomapi.tools.action"].ApiSuccessNotification(msg)
                elif wecomapi.expiration_time > datetime.now():
                    # 令牌未过期，则直接返回 提示信息
                    msg = {
                        "title": _("Tips"),
                        "message": _(
                            "Token is still valid, and no update is required!"
                        ),
                        "sticky": False,
                    }
                    # return self.env["wecomapi.tools.action"].ApiInfoNotification(msg)
                else:
                    # 令牌已过期，则重新获取
                    res.write(
                        {
                            "access_token": wecomapi.access_token,
                            "expiration_time": wecomapi.expiration_time,
                        }
                    )
                    msg = {
                        "title": _("Tips"),
                        "message": _("The access token was successfully obtained!"),
                        "sticky": False,
                    }
                    # return self.env["wecomapi.tools.action"].ApiSuccessNotification(msg)