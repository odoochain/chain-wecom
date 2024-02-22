# -*- coding: utf-8 -*-
{
    "name": "WeChat Message",
    "author": "RStudio",
    "sequence": 708,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeChat Suites/Message",
    "version": "16.0.0.1",
    "summary": """
Odoo event notification to Wechat.
        """,
    "description": """
Odoo event notification to Wechat.
        """,
    "depends": ["mail", "wechat_base", "wechat_official_accounts"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wechat_compose_message_views.xml",
        "views/res_config_settings_views.xml",
        "views/wechat_message_templates_views.xml",
        "views/wechat_message_template_list_views.xml",
        "views/menu_views.xml",
    ],
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "assets": {
        "web.assets_frontend": [],
        "web.assets_backend": [
            "wechat_message/static/src/views/**/*.js",
            "wechat_message/static/src/views/**/*.xml",
        ],
    },
    "license": "Other proprietary",
}
