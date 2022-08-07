# -*- coding: utf-8 -*-

{
    "name": "HRMS",
    "author": "RStudio",
    "sequence": 501,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom/WeCom",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "version": "14.0.0.2",
    "summary": "Human Resource Management System",
    "description": """

        """,
    "depends": ["hr",
                "hr_work_entry_contract",
                "hr_skills",
                "hr_appraisal",
                "pl_wecom_widget",
                ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        # "data/hr_data.xml",
        "wizard/hr_plan_wizard_views.xml",
        # "wizard/hr_menu_wizard_views.xml",
        "views/ir_ui_menu_views.xml",
        "views/assets.xml",
        "views/res_config_settings_views.xml",
        "views/hr_department_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_employee_category_views.xml",
        "views/menu_views.xml",
    ],
    'qweb': [
        'static/src/xml/hr_settings_navigation_menu.xml',
    ],
    "external_dependencies": {"python": [],},
    "license": "LGPL-3",
    "bootstrap": True,
}
