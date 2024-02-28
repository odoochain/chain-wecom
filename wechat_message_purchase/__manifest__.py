# -*- coding: utf-8 -*-
{
    "name": "WeChat Message:Purchase",
    "author": "RStudio",
    "sequence": 708,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeChat Suites/Message",
    "version": "16.0.0.1",
    "summary": """
Send purchase orders, tenders and agreement messages to WeChat users.
        """,
    "description": """
Send purchase orders, tenders and agreement messages to WeChat users.
        """,
    "depends": ["wechat_message", "buy",],
    "data": [
        # "security/ir.model.access.csv",
        # "data/wechat_message_data.xml",
        # "views/res_config_settings_views.xml",
        # "views/purchase_views.xml",
    ],
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "assets": {
        "web.assets_frontend": [],
    },
    "license": "Other proprietary",
}
