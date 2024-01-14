# -*- coding: utf-8 -*-
{
    "name": "WeChat Customer Portal",
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
    "depends": ["portal","wechat_base"],
    "data": [

    ],
    "bootstrap": True,  # 加载登录屏幕的翻译，
    "assets": {
        "web.assets_frontend": [
            'wechat_portal/static/**/*.js',
            'wechat_portal/static/**/*.xml',
            'wechat_portal/static/**/*.scss',
        ],

    },

    "license": "Other proprietary",
}
