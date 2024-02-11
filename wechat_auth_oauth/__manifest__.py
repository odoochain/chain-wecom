# -*- coding: utf-8 -*-
{
    "name": "WeChat OAuth2 Authentication",
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
    "depends": ["web","auth_password_policy","auth_oauth","wechat_base"],
    "data": [
        "data/wechat_oauth_data.xml",
        "views/res_config_settings_views.xml",
        "views/auth_signup_login_templates.xml",
    ],
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "assets": {
        "web.assets_frontend": [
            'wechat_auth_oauth/static/**/*.js',
            'wechat_auth_oauth/static/**/*.xml',
            'wechat_auth_oauth/static/**/*.scss',
        ],

    },

    "license": "Other proprietary",
}
