# -*- coding: utf-8 -*-
from odoo import http, api, SUPERUSER_ID
import werkzeug.utils
from werkzeug.exceptions import BadRequest
from odoo import SUPERUSER_ID, api, http, _
from odoo import registry as registry_get
import os
import sys
import logging

from lxml import etree

from odoo import http
from odoo.addons.wechat.models.Corpapi import Corpapi, CORP_API_TYPE
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException
from odoo.http import request

_logger = logging.getLogger(__name__)


class WechatController(http.Controller):
    @http.route("/wechat/callback", methods=["POST"], auth="public", type="http", csrf=False)
    def wechat_callback(self):
        xml_raw = request.httprequest.get_data().decode(request.httprequest.charset)
        _logger.debug(
            "/wechat/callback request data: %s\nheaders %s: ",
            xml_raw,
            request.httprequest.headers,
        )

        # convert xml to object
        xml = etree.fromstring(xml_raw)
        data = {}
        for child in xml:
            data[child.tag] = child.text

        res = request.env["wechat.order"].sudo().on_notification(data)

        if res is not False:
            return """<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"""
        else:
            return """<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[Signature failure]]></return_msg></xml>"""

    @http.route('/wechat/open/', auth='public')
    def open_wechat(self):
        """
        企业微信扫码登录oauth_url
        1.构造独立窗口登录二维码
            https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid=CORPID&agentid=AGENTID&redirect_uri=REDIRECT_URI&state=STATE

        """
        # request.httprequest.user_agent = 'Mozilla/5.0 (Linux; Android 5.0; SM-N9100 Build/LRX21V) > AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 > Chrome/37.0.0.0 Mobile Safari/537.36 > MicroMessenger/6.0.2.56_r958800.520 NetType/WIFI'
        # print(request.httprequest.user_agent)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 当前程序上上一级目录，这里为mycompany
        sys.path.append(BASE_DIR)  # 添加环境变量

        dbname = request.session.db
        registry = registry_get(dbname)
        with registry.cursor() as cr:
            try:
                # 设置odoo运行环境
                env = api.Environment(cr, SUPERUSER_ID, {})
                config = env['wechat.corp.config'].sudo().browse(1)[0]
                if config:
                    # 获取url参数
                    corp_id = config.corp_id
                    agent_id = config.corp_agent
                    redirect_url = 'http://127.0.0.1:8088/wechat/ouath/'
                    state = 'weblogin@gyoss9'
                    # 获取服务器域名
                    host = request.httprequest.environ.get('HTTP_HOST', '')
                    # 拼接获取企业微信code参数的url
                    url = 'https://open.work.weixin.qq.com/wwopen/sso/qrConnect?appid=%s&agentid=%s&redirect_uri=%s&state=%s' % (corp_id, agent_id, redirect_url, state)

            except Exception as e:
                _logger.exception("open: %s" % str(e))
                url = "/web/login?oauth_error=2"

        return self.set_cookie_and_redirect(url)

    @http.route('/wechat/ouath/', auth='public')
    def ouath_wechat(self, **kwargs):
        """ 扫码后的redirect_url """
        code = request.params.get('code')
        dbname = request.session.db
        registry = registry_get(dbname)
        with registry.cursor() as cr:
            try:
                env = api.Environment(cr, SUPERUSER_ID, {})
                config = env['wechat.corp.config'].sudo().search([('id', '=', 1)])[0]
                if config:
                    corp_id = config.corp_id
                    corp_agent_secret = config.corp_agent_secret

            except Exception as e:
                _logger.exception("oauth: %s" % str(e))

        # 调用企业微信api
        if code and corp_id and corp_agent_secret:
            wx_api = Corpapi(corp_id, corp_agent_secret)
            try:
                # 获取access_token
                accesstoken = wx_api.getAccessToken()
                # 获取user info
                response = wx_api.httpcall(
                    CORP_API_TYPE['GET_USER_INFO_BY_CODE'],
                    {
                        'code': code
                    }
                )
                _logger.info(u'UserId%s' %response.get('UserId'))

                if response['UserId']:
                    with registry.cursor as cr:
                        try:
                            env = api.Environment(cr, SUPERUSER_ID, {})
                            wechat_corp_users_id = env['wecom.users'].sudo().search([('wecom_userid', '=', response['UserId'])])[0]
                            res_users_id = env['res.users'].sudo().search([('wxcorp_users_id', '=', wechat_corp_users_id.id)])[0]
                            login = res_users_id.login
                            if login:
                                # 更新访问令牌
                                res_users_id.write({
                                    'oauth_access_token': accesstoken
                                })
                                cr.commit()
                                # 验证核心函数authenticate：dbname,login,passwd或者访问令牌
                                request.session.authenticate(dbname, login, accesstoken)
                                url = '/web'

                            else:
                                url = '/web/login?oauth_error=2'

                        except Exception as e:
                            _logger.exception("oauth_res_users: %s" % str(e))
                            url = '/web/login?oauth_error=2'

            except ApiException as e:
                # print e.errCode, e.errMsg
                _logger.info(u'errMsg:%s' % e.errMsg)

        else:
            url = '/web/login?oauth_error=2'

        return self.set_cookie_and_redirect(url)

    def set_cookie_and_redirect(self, redirect_url):
        """ 跳转url """
        redirect = werkzeug.utils.redirect(redirect_url, 303)
        redirect.autocorrect_location_header = False
        return redirect