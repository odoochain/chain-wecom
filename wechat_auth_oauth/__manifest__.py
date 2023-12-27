# -*- coding: utf-8 -*-
{
    "name": "WeChat Authentication",
    "author": "RStudio",
    "sequence": 705,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeChat Suites/Authentication",
    "version": "16.0.0.1",
    "summary": """
Allow users to log in through WeChat.
        """,
    "description": """
Allow users to log in through WeChat.
        """,
    "depends": ["portal", "auth_oauth","wechat_base"],
    "data": [
        "data/wechat_oauth_data.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "wechat_auth_oauth/static/src/webclient/**/*",
        ],
        "web.assets_frontend": [
            "wechat_auth_oauth/static/src/frontend/**/*",
        ],
    },
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "license": "Other proprietary",
}
