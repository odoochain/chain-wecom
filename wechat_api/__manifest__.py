# -*- coding: utf-8 -*-
{
    "name": "Wechat API",
    "author": "RStudio",
    "website": "https://gitee.com/rainbowstudio/wecom",
    "sequence": 700,
    "installable": True,
    "application": False,
    "auto_install": False,
    "category": "WeChat Suites/Settings",
    "version": "16.0.0.1",
    "summary": """
        """,
    "description": """

        """,
    "depends": [],
    "data": [
        "security/ir.model.access.csv",
        "data/wechat_error_codes_dara.xml",
    ],
    "assets": {
        "web.assets_common": [
            # JS
            # "wecom_api/static/src/js/*.js",
        ],
        "web.assets_backend": [
            # JS
        ],
    },
    "external_dependencies": {
        "python": [
            "xmltodict",
            "pycryptodome",
            "html2text",
        ],
    },
    "license": "Other proprietary",
}
