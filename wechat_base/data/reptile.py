# -*- coding: utf-8 -*-


# ----------------------------------------
#   使用爬虫爬取微信错误码 生成 XML 数据文件
# ----------------------------------------

import requests
import pandas as pd
from lxml import etree, builder, objectify
import xml.etree.ElementTree as ET


# nodes = "//div[hasclass('table-wrp')]"
nodes = "//table/tbody/tr"
url = "https://developers.weixin.qq.com/doc/oplatform/Return_codes/Return_code_descriptions_new.html"
page_text = requests.get(url=url).text
tree = etree.HTML(page_text)  # type: ignore
lines = tree.xpath(nodes)


# 输出一个错误代码列表
codes = []
for line in lines:
    code = line.xpath("./td[1]/text()")[0]
    try:
        name = line.xpath("./td[2]/text()")[0]
    except:
        name = line.xpath("./td[3]/text()")[0]

    # xml 转义
    if '"' in name:
        name.replace('"', "&quot;")
    if "&" in name:
        name.replace('"', "&amp;")
    if "<" in name:
        name.replace('"', "&lt;")
    if "<" in name:
        name.replace(">", "&gt;")
    codes.append(
        {
            "code": int(code),
            "name": name,
        }
    )

# 排序
new_codes = sorted(codes, key=lambda c: int(c["code"]))

# ----------------------------
# https://docs.python.org/zh-cn/3/library/xml.etree.elementtree.html#building-xml-documents
# https://www.blog.pythonlibrary.org/2014/03/26/python-creating-xml-with-lxml-objectify/
# https://lxml.de/tutorial.html
# ----------------------------
# 生成生成根节点
root = etree.Element("odoo")  # type: ignore

# 生成 data 节点
data_node = etree.Element("data",attrib={"noupdate":"0"})  # type: ignore
root.append(data_node)

for code in new_codes:
    Field = builder.E.field

    id = "wechat_error_codes_"
    if code == -1:
        id += "minus_1"
    else:
        id += str(code["code"])

    record_attrs = {
        "id": id,
        "model": "wechat.error_codes",
    }
    record = etree.Element("record", attrib=record_attrs)  # type: ignore
    # record.append(Field(name, name='name'))
    data_node.append(record)

# 将这个xml树写进test.xml
# tree.write('test.xml', encoding='utf-8', xml_declaration=True)
# print(etree.tostring(root))


def prettyprint(element, **kwargs):
    xml = etree.tostring(element, pretty_print=True, **kwargs) # type: ignore
    print(xml.decode(), end='')

prettyprint(root)