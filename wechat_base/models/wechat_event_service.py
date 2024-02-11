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
            print("订阅事件")
            return self.handle_subscribe(even_dict["Event"],data["openid"])
        else:
            print("非订阅事件")

        #^ 微信服务器在五秒内收不到响应会断掉连接，并且重新发起请求，总共重试三次。
        #^ 假如服务器无法保证在五秒内处理并回复，可以直接回复空串，微信服务器不会对此作任何处理，并且不会发起重试。
        return ""

    def handle_subscribe(self, type, openid):
        """
        处理 订阅事件 和 取消订阅事件
        """
        # 获取用户的的 unionid
        UserSudo = self.env["res.users"].sudo()
        user = UserSudo.search(
            [
                "|",
                ("wechat_open_platform_openid", "=", openid),
                ("wechat_official_account_openid", "=", openid),
                "|",
                ("active", "=", True),
                ("active", "=", False),
            ],
            limit=1,
        )
        print(user, self.app_id.access_token,)
        if (not user) and (type =="subscribe"):
            # 文档：https://developers.weixin.qq.com/doc/offiaccount/User_Management/Get_users_basic_information_UnionID.html#UinonId
            # 不存在用户且为订阅事件,创建用户
            # get_userinfo_url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN" % (self.app_id.access_token, openid)
            # try:
            #     userinfo = requests.get(get_userinfo_url).json()
            # except Exception as e:
            #     print(str(e))
            # else:
            #     print(userinfo)
            #     ICP = self.env["ir.config_parameter"].sudo()
            #     user_company = ICP.get_param("wechat_default_user_company")
            #     values ={
            #         "name": userinfo["unionid"],
            #         "login": userinfo["unionid"],
            #         "active":True,
            #         "password": self.env["wechat.tools.security"].random_passwd(8),
            #         "company_ids": [(6, 0, [int(user_company)])],
            #         "company_id": int(user_company),
            #         # 以下为微信专有字段
            #         "is_wechat_user": True,
            #         "wechat_unionid": userinfo["unionid"],
            #         "wechat_official_account_openid": userinfo["openid"],
            #     }
            # TODO 日后在处理
            pass

        elif user and type =="subscribe":
            # 存在用户,且为订阅事件,激活用户
            user.update({
                "active":True
            })
        elif user and type =="unsubscribe":
            # 存在用户,且为取消订阅事件,归档用户
            user.update({
                "active":False
            })
        return ""