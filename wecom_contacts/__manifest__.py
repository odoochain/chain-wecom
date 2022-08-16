# -*- coding: utf-8 -*-
{
    "name": "WeCom Contacts",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 602,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "version": "14.0.0.3",
    "summary": """
        WeCom Contacts
        """,
    "description": """


        """,
    "depends": [
        "hrms_base",
        "contacts",
        "hr",
        "wecom_base",
        "pl_wecom_widget",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/assets_templates.xml",
        "data/ir_cron_data.xml",
        "data/wecom_apps_data.xml",
        "views/res_partner_views.xml",
        "views/res_partner_category_views.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/ir_cron_views.xml",
        "views/menu_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml", ],
    # "pre_init_hook": "pre_init_hook",
    "license": "LGPL-3",
}
