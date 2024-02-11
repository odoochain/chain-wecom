# -*- coding: utf-8 -*-
{
    "name": "WeChat Official Accounts H5 Website - Sales",
    "author": "RStudio",
    "sequence": 708,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeChat Suites/Portal",
    "version": "16.0.0.1",
    "summary": """
Build sales related pages for WeChat official account.
        """,
    "description": """
Build sales related pages for WeChat official account.
        """,
    "depends": [
        "wechat_web",
        "sale",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/sale_portal_templates.xml",
    ],
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "assets": {
        "web.assets_frontend": [
            "wechat_web_sale/static/**/*.js",
            "wechat_web_sale/static/**/*.xml",
            "wechat_web_sale/static/**/*.scss",
        ],
    },
    "license": "Other proprietary",
}
