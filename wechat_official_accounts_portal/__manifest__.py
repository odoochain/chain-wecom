# -*- coding: utf-8 -*-
{
    "name": "WeChat Official Accounts Portal",
    "author": "RStudio",
    "sequence": 707,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeChat Suites/Portal",
    "version": "16.0.0.1",
    "summary": """
Allow users to log in through WeChat.
        """,
    "description": """
Allow users to log in through WeChat.
        """,
    "depends": ["web", "portal", "wechat_official_accounts", "wecom_auth_oauth"],
    "data": [
        "security/ir.model.access.csv",
        "data/wechat_official_accounts_menus_data.xml",
        "views/res_config_settings_views.xml",
        "views/wechat_official_accounts_menus_views.xml",
        "views/wechat_applications_views.xml",
        "views/menu_views.xml",
        "templates/webclient.xml",
    ],
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "assets": {
        "web.assets_frontend": [
            "wechat_portal/static/**/*.js",
            "wechat_portal/static/**/*.xml",
            "wechat_portal/static/**/*.scss",
        ],
    },
    "license": "Other proprietary",
}
