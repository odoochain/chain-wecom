# -*- coding: utf-8 -*-
{
    "name": "WeChat Official Accounts H5 Website",
    "author": "RStudio",
    "sequence": 707,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeChat Suites/Portal",
    "version": "16.0.0.1",
    "summary": """
Build menus and pages for WeChat official accounts.
        """,
    "description": """
Build menus and pages for WeChat official accounts.
        """,
    "depends": ["web", "portal", "wechat_official_accounts", "wechat_auth_oauth"],
    "data": [
        "security/ir.model.access.csv",
        "data/wechat_official_accounts_menus_data.xml",
        "views/wechat_official_accounts_menus_views.xml",
        "views/wechat_applications_views.xml",
        "views/res_config_settings_views.xml",
        "views/webclient_templates.xml",
        "views/portal_templates.xml",
        "views/menu_views.xml",
    ],
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "assets": {
        "web.assets_frontend": [
            "wechat_web/static/**/*.js",
            "wechat_web/static/**/*.xml",
            "wechat_web/static/**/*.scss",
            "https://res.wx.qq.com/t/wx_fed/weui-source/res/2.6.11/weui.min.css",
        ],
    },
    "license": "Other proprietary",
}
