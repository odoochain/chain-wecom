# -*- coding: utf-8 -*-

import json
import logging
import xml.etree.cElementTree as ET
from lxml import etree
import sys
from odoo.addons.wecom_api.api.wecom_msg_crtpt import WecomMsgCrypt  # type: ignore
from odoo import http, models, fields, _
from odoo.http import request
from odoo.http import Response

_logger = logging.getLogger(__name__)


class WeChatMessagePushServer(http.Controller):
    """
    微信消息推送服务
    """

    def OpenPlatformAuthorizedUserInformationChangeEvent(self, **kw):
        """
        授权用户信息变更事件
        1、 授权用户资料变更：当部分用户的资料存在风险时，平台会对用户资料进行清理，并通过消息推送服务器通知最近30天授权过的公众号开发者，我们建议开发者留意响应该事件，及时主动更新或清理用户的头像及昵称，降低风险。
        2、 授权用户资料撤回：当用户撤回授权信息时，平台会通过消息推送服务器通知给公众号开发者，请开发者注意及时删除用户信息。
        3、 授权用户完成注销：当授权用户完成注销后，平台会通过消息推送服务器通知给公众号开发者，请依法依规及时履行相应个人信息保护义务，保护用户权益
        """

