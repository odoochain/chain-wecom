# -*- coding: utf-8 -*-
{
    "name": "WeCom Employee Portal",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 606,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.2",
    "summary": """
        WeCom Employee Portal
        """,
    "description": """


        """,
    "depends": [
        "wecom_message",
        "portal",
    ],
    "external_dependencies": {"python": [],},
    "data": [
        "data/wecom_apps_data.xml",
        "views/portal_templates.xml",
        "views/res_config_settings_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml",],
}
