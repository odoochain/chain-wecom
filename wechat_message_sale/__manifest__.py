# -*- coding: utf-8 -*-
{
    "name": "WeChat Message:Sales",
    "author": "RStudio",
    "sequence": 708,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeChat Suites/Message",
    "version": "16.0.0.1",
    "summary": """
Send sales quotations and order messages to WeChat users.
        """,
    "description": """
Send sales quotations and order messages to WeChat users.
        """,
    "depends": ["wechat_message", "sale"],
    "data": [
        "data/wechat_message_data.xml",
        "views/res_config_settings_views.xml",
    ],
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "assets": {
        "web.assets_frontend": [],
    },
    "license": "Other proprietary",
}
