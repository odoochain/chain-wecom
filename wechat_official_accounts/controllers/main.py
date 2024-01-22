# -*- coding: utf-8 -*-

import hashlib
import json
import logging
from odoo import api, http, SUPERUSER_ID, _
from odoo.http import request,Response
from odoo.addons.wechat_base.controllers.main import WeChatMessagePushServer as WMPS  # type: ignore
from odoo.addons.wechat_api.api.WXBizMsgCrypt import WXBizMsgCrypt,SHA1  # type: ignore

_logger = logging.getLogger(__name__)

class WeChatOfficialAccountMessagePushService(WMPS):

    @http.route('/wechat/event/official_account', type="http",
        auth="public",
        methods=["GET", "POST"],
        csrf=False,)
    def OfficialAccountAuthorizedUserInformationChangeEvent(self, **kw):
        """
        授权用户信息变更事件
        1、 授权用户资料变更：当部分用户的资料存在风险时，平台会对用户资料进行清理，并通过消息推送服务器通知最近30天授权过的公众号开发者，我们建议开发者留意响应该事件，及时主动更新或清理用户的头像及昵称，降低风险。
        2、 授权用户资料撤回：当用户撤回授权信息时，平台会通过消息推送服务器通知给公众号开发者，请开发者注意及时删除用户信息。
        3、 授权用户完成注销：当授权用户完成注销后，平台会通过消息推送服务器通知给公众号开发者，请依法依规及时履行相应个人信息保护义务，保护用户权益。

        ----------------------------------------------------------------------------
        参数	    描述
        signature   微信加密签名，signature结合了你在上面填写的自定义的Token参数和请求中的timestamp参数、nonce参数。
        timestamp   时间戳
        nonce       随机数
        echostr     随机字符串
        ----------------------------------------------------------------------------
        """
        print(kw)
        event_service = request.env["wechat.event_service"].sudo().search([("route", "=", "/wechat/event/official_account")])
        if event_service.active is False:
            _logger.info(
                _("App [%s] did not start the event service")% event_service.name
            )
            return Response("success", status=200)
        else:
            decrypt = WXBizMsgCrypt(
                event_service.token,
                event_service.aeskey,
                event_service.app_id.appid,
            )

            # 获取微信发送的相关参数
            sVerifyMsgSig = kw["signature"]
            sVerifyTimeStamp = kw["timestamp"]
            sVerifyNonce = kw["nonce"]
            sVerifyEchoStr = kw["echostr"]

            if request.httprequest.method == "GET":
                # 开发者接收到这(signature,timestamp,nonce,echostr)之后，根据【一定的规则】生成一个signature，跟微信服务器发过来的signature进行对比，一致则说明此次GET请求来自微信服务器，原样返回echostr参数内容，接入生效，成为开发者成功，否则接入失败。
                # 规则如下：

                # 1. 将token、timestamp、nonce三个参数进行字典序排序
                temp = [sVerifyTimeStamp, sVerifyNonce, event_service.token]
                temp.sort()

                # 2. 将三个参数字符串拼接成一个字符串进行sha1加密
                temp = "".join(temp)

                # 3. 开发者获得加密后的字符串可与signature对比，标识该请求来源于微信
                if (hashlib.sha1(temp.encode('utf8')).hexdigest() == sVerifyMsgSig):
                    # print("验证成功")
                    _logger.info(_("The server configuration of [%s] was successfully verified.")% event_service.name)
                    return sVerifyEchoStr
                else:
                    # print("验证失败")
                    _logger.info(_("The WeChat official account server configuration verification of [%s] failed.")% event_service.name)
                    return Response("Not Found", status=404)
            if request.httprequest.method == "POST":
                pass
