# -*- coding: utf-8 -*-
{
    "name": "WeChat Base",
    "author": "RStudio",
    "sequence": 701,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeChat Suites/Settings",
    "version": "16.0.0.1",
    "summary": """
        """,
    "description": """
        """,
    "depends": ["base_setup", "wechat_api"],
    "data": [
        "security/wechat_security.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/res_users_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [],
        "web.assets_frontend": [],
    },
    "license": "Other proprietary",
}
