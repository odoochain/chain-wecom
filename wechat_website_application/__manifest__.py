# -*- coding: utf-8 -*-
{
    "name": "WeChat Website Application",
    "author": "RStudio",
    "sequence": 704,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeChat Suites/Settings",
    "version": "16.0.0.1",
    "summary": """
        """,
    "description": """
        """,
    "depends": ["auth_oauth","wechat_base",],
    "data": [
        "data/wechat_oauth_data.xml",
        "data/wechat_applications_data.xml",
        "data/wechat_event_service_data.xml",
        "views/res_config_settings_views.xml",
        "views/wechat_users_views.xml",
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [],
        "web.assets_frontend": [],
    },
    "license": "Other proprietary",
}