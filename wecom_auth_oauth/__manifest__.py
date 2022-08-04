# -*- coding: utf-8 -*-
{
    "name": "WeCom Authentication",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 604,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.2",
    "summary": """
        One click login, code scanning login.
        """,
    "description": """

        """,
    "depends": [
        "portal",
        "auth_oauth",
        "wecom_material",
        "wecom_base",
    ],
    "data": [
        "data/wecom_apps_data.xml",
        "data/wecom_app_config_data.xml",
        "data/wecom_oauth_data.xml",
        # "data/wecom_oauth_data.xml",
        "views/assets_templates.xml",
        "views/res_config_settings_views.xml",
        "views/wecom_apps_views.xml",
        "views/auth_signup_login_templates.xml",
        # "views/menu_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml", ],
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "license": "LGPL-3",
}
