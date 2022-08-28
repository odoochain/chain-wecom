# -*- coding: utf-8 -*-


import requests
import logging
from urllib.parse import quote, unquote
import pandas as pd

pd.set_option("max_colwidth", 4096)

from lxml import etree
import requests
from odoo import api, fields, models, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class WecomServerApiError(models.Model):
    _name = "wecom.service_api_error"
    _description = "Wecom Server API Error"
    _order = "sequence"

    name = fields.Char("Error description", required=True, readonly=True,)
    code = fields.Integer("Error code", required=True, readonly=True,)

    method = fields.Char("Treatment method", readonly=True,)

    sequence = fields.Integer(default=0)

    def get_error_by_code(self, code):
        res = self.search([("code", "=", code)], limit=1,)
        return {
            "code": res.code,
            "name": res.name,
            "method": res.method,
        }

    def cron_pull_global_error_code(self):
        self.pull()

    @api.model
    def pull(self):
        """
        使用爬虫爬取 全局错误码
        URL的一般格式为： protocol://hostname[:port]/path/[;parameters][?query]#fragment
        """
        ir_config = self.env["ir.config_parameter"].sudo()
        global_error_code_url = ir_config.get_param("wecom.global_error_code_url")
        global_error_code_troubleshooting_method_node = ir_config.get_param("wecom.global_error_code_troubleshooting_method_node")
        try:
            _logger.info(_("Start pulling the global error code of WeCom."))
            # url = "https://developer.work.weixin.qq.com/document/path/90313"  # 2022-05-29
            page_text = requests.get(url=global_error_code_url).text
            tree = etree.HTML(page_text)

            # 生成 排查方法, 企业全局错误码 页面最下面的 “排查方法” 内容
            # methods_elements = tree.xpath("//ul[@data-sign='07e2431b7bbf7440a0301c13cc9c5afa']/li") # 
            methods_elements = tree.xpath(global_error_code_troubleshooting_method_node) # 2022-06-27

            methods = []

            for element in methods_elements:
                code_str = element.text
                code = code_str.split("：",1)[1:][0]

                element_str = etree.tostring(
                    element, encoding="utf-8", pretty_print=True
                ).decode()
                
                code_str = "%s<br/>" % code_str
                method_str = element_str.replace(code_str, "")
                method = self.getMiddleStr(method_str,"<li>","</li>")
                if " " in code:
                    # 一个元素存在多个错误码
                    multiple_codes = code.split(" ", 1)
                    for multiple_code in multiple_codes:
                        multiple_dic = {}
                        multiple_dic["code"] = multiple_code
                        multiple_dic["method"] = method

                        methods.append(multiple_dic)
                else:
                    dic = {}
                    dic["code"] = code
                    dic["method"] = method

                    methods.append(dic)
   
            table = tree.xpath("//div[@class='cherry-table-container']/table")  # 取出表格
            table = etree.tostring(
                table[0], encoding="utf-8"
            ).decode()  # 将第一个表格转成string格式
            table = table.replace("<th>错误码</th>", "<th>code</th>")
            table = table.replace("<th>错误说明</th>", "<th>name</th>")
            table = table.replace("<th>排查方法</th>", "<th>method</th>")

            df = pd.read_html(table, encoding="utf-8", header=0)[0]  # pandas读取table

            error_results = list(df.T.to_dict().values())  # 转换成列表嵌套字典的格式

            errors = []
            for index, error in enumerate(error_results):
                # del error["Unnamed: 3"]
                error["sequence"] = index
                if error["method"] == "查看帮助":
                    error["method"] = self.replaceMethod(str(error["code"]), methods)
                errors.append(error)

            # 写入到odoo
            for error in errors:
                res = self.search([("code", "=", error["code"])], limit=1,)
                if not res:
                    self.sudo().create(
                        {
                            "code": error["code"],
                            "name": error["name"],
                            "method": error["method"],
                            "sequence": error["sequence"],
                        }
                    )
                else:
                    res.sudo().write(
                        {
                            "name": error["name"],
                            "method": error["method"],
                            "sequence": error["sequence"],
                        }
                    )
            msg = _("Successfully pulled the WeCom global error code!")
            _logger.info(msg)
            return {"state":True, "msg":msg}
        except Exception as e:
            msg = _("Failed to pull WeCom global error code, reason:%s") % str(e)
            _logger.warning(msg)
            return {"state":False, "msg":msg}

    def replaceMethod(self, code, methods):
        """ 
        替换 排查方法
        """
        df = pd.DataFrame(methods)
        method = df["method"][df["code"] == code].to_string(
            index=False
        )  # 取 包含指定code 值的 "method"列

        return method

    def getMiddleStr(self, content, startStr, endStr):
        startIndex = content.index(startStr)
        if startIndex >= 0:
            startIndex += len(startStr)
        endIndex = content.index(endStr)
        return content[startIndex:endIndex]
