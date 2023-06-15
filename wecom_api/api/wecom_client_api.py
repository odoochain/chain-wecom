# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime, timedelta
import time
from odoo import api, fields, models, SUPERUSER_ID, _
from collections import OrderedDict

class WecomClientApi(models.TransientModel):
    _name = "wecom.client_api"
    _description = "Wecom Client API"

    @api.model
    def geContactsDisplayAgentConfig(self, postDatas):
        """
        获取企业微信通讯录展示组件的应用配置
        """
        configs = []
        result = {}
        for data in postDatas:
            config = {}
            company =  self.env['res.company'].search([('id','=',data['company_id'])])
            self_built_app = company.self_built_app_id

            timestamp = int(time.time())
            nonceStr = self.env["wecomapi.tools.security"].random_str(8)
            jsapi_ticket = company.contacts_app_id.jsapi_ticket
            signature = self.env["wecomapi.tools.security"].generate_jsapi_signature(jsapi_ticket,nonceStr,timestamp)

            config.update({
                "company_id":company.id,
                "corpid":company.corpid,
                "agentid":self_built_app.agentid,
                "timestamp":timestamp,
                "nonceStr":nonceStr,
                "signature":signature,
                "jsApiList":['selectExternalContact'],
                
            })
            configs.append(config)
        result.update({
            "code":0,
            "msg":"ok",
            "configs":configs,
        })
        return result