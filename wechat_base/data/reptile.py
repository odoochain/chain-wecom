#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------
#   使用爬虫爬取微信错误码 生成 XML 数据文件
# ----------------------------------------
import os
from io import BytesIO
import requests
from lxml import etree


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
        # print(name)

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
# https://lxml.de/tutorial.html
# ----------------------------
# 生成生成根节点
root = etree.Element("odoo")  # type: ignore

# 生成 data 节点
data_node = etree.Element("data", attrib={"noupdate": "0"})  # type: ignore
root.append(data_node)

for code in new_codes:
    id = "wechat_error_codes_"
    if code == -1:
        id += "minus_1"
    else:
        id += str(code["code"])

    record_attrs = {
        "id": id,
        "model": "wechat.error_codes",
    }
    record_node = etree.Element("record", attrib=record_attrs)  # type: ignore

    code_field_node = etree.Element("field", attrib={"name": "code"})  # type: ignore
    code_field_node.text = str(code["code"])
    name_field_node = etree.Element("field", attrib={"name": "name"})  # type: ignore
    name_field_node.text = code["name"]
    record_node.append(code_field_node)
    record_node.append(name_field_node)
    data_node.append(record_node)

# 保存xml
xml = (
    """<?xml version="1.0" encoding="utf-8"?>
%s
"""
    % etree.tostring(root, pretty_print=True).decode()
)


current_dir = os.path.dirname(os.path.abspath(__file__))
xml_file_name = "reptile.xml"
xml_file_path = os.path.join(current_dir, xml_file_name)

if not os.path.exists(xml_file_path):
    os.system(r"touch {}".format(xml_file_path))  # 调用系统命令行来创建文件

with open(xml_file_path, "w", encoding="gb2312") as f:
    f.write(xml)
