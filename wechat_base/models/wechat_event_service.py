# -*- coding: utf-8 -*-

import requests # type: ignore
import xmltodict
from odoo import api, fields, models, SUPERUSER_ID, _

class WechatEventService (models.Model):
    """
    微信事件服务
    """
    _name = "wechat.event_service"
    _description = "WeChat event service"

    app_id = fields.Many2one(
        "wechat.applications",
        string="Application",
        copy=False,
        ondelete="cascade",
        default=lambda self: self.env["wechat.applications"].id,
        # domain="[('company_id', '=', company_id)]",
        required=True,
    )
    name = fields.Char(string="Service Name", required=True, translate=True)
    service_type = fields.Selection(
        string='Service Type',
        required=True,
        selection=[('official_account', 'Official Account'), ('open_platform', 'Open platform')]
    )

    route = fields.Char(string="Route", required=True, translate=False)
    url = fields.Char(
        string="URL",
        store=True,
        readonly=True,
        compute="_default_url",
        copy=False,
    )  # 回调服务地址
    token = fields.Char(string="Token", copy=False)  # Token用于计算签名
    aeskey = fields.Char(string="AES Key", copy=False)  # 用于消息内容加密
    description = fields.Text(string="Description", translate=True, copy=True)
    active = fields.Boolean("Active", default=False)

    @api.depends("route")
    def _default_url(self):
        params = self.env["ir.config_parameter"].sudo()
        base_url = params.get_param("web.base.url")
        for service in self:
            service.url = base_url + service.route

    _sql_constraints = [("route_uniq", "unique (route)", _("route must be unique !"),)]


    def handle_event(self):
        """
        处理事件
        """
        data = self.env.context.get("data")
        print("事件openid",data["openid"])
        even_dict = xmltodict.parse(data["xml"])["xml"]
        print("事件xml",even_dict)

        if even_dict["Event"]=="subscribe" or even_dict["Event"]=="unsubscribe":
            self.handle_subscribe(even_dict["Event"],data["openid"])

        #^ 微信服务器在五秒内收不到响应会断掉连接，并且重新发起请求，总共重试三次。
        #^ 假如服务器无法保证在五秒内处理并回复，可以直接回复空串，微信服务器不会对此作任何处理，并且不会发起重试。
        return ""

    def handle_subscribe(self, type, openid):
        """
        处理 订阅事件 和 取消订阅事件
        """
        # 获取用户的的 unionid
        get_userinfo_url ="https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN" % (self.app_id.access_token,openid)
        userinfo = requests.get(get_userinfo_url).json()
        print(userinfo)
        if type =="subscribe":
            # 创建用户
            pass
        elif  type =="unsubscribe":
            # 停用用户
            pass