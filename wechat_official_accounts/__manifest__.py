# -*- coding: utf-8 -*-
{
    "name": "WeChat Official Accounts",
    "author": "RStudio",
    "sequence": 703,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeChat Suites/Settings",
    "version": "16.0.0.1",
    "summary": """
        """,
    "description": """
        """,
    "depends": ["mass_mailing","auth_oauth","wechat_base"],
    "data": [
        "data/res_company_data.xml",
        "data/wechat_oauth_data.xml",
        "data/wechat_applications_data.xml",
        "data/wechat_event_service_data.xml",
        "views/res_config_settings_views.xml",
        "views/social_media_sidebar.xml",
    ],
    "assets": {
        "web.assets_backend": [],
        "web.assets_frontend": [
            # 'wechat_official_accounts/static/**/*.js',
            # 'wechat_official_accounts/static/**/*.xml',
            # 'wechat_official_accounts/static/**/*.scss',
        ],
    },
    "license": "Other proprietary",
}
