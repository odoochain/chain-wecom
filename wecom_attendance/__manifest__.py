# -*- coding: utf-8 -*-

{
    "name": "WeCom Attendances",
    "author": "RStudio",
    "sequence": 610,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/Attendances",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "version": "14.0.0.2",
    "summary": """
        
        """,
    "description": """

        """,
    "depends": [
        "wecom_contacts",
        "hrms_base",
        "wecom_contacts_sync",
        "hrms_attendance",],
    "data": [
        "security/ir.model.access.csv",
        "data/wecom_apps_data.xml",
        "views/assets_templates.xml",
        "views/res_config_settings_views.xml",
        "views/wecom_checkin_rule_views.xml",
        "wizard/wecom_checkin_rules_wizard_views.xml",
        "views/menu_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml", ],
    "license": "LGPL-3",
}
