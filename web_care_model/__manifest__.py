# -*- coding: utf-8 -*-


{
    "name": "Login page care mode",
    "author": "RStudio",
    "category": "Website/Website",
    "sequence": 21,
    "summary": "Web care mode",
    "description": """The text is larger and clearer.
Stronger colors for better recognition.
The button is larger and easier to use.
     """,
    "website": "",
    "version": "16.0.0.1",
    "depends": [
        "web",
    ],
    "installable": True,
    "application": True,
    "data": [],
    "assets": {
        "web.assets_frontend": [
            "web_care_model/static/src/legacy/**/*",
        ],
        "web.assets_backend": [
            "web_care_model/static/src/webclient/**/*",
        ]
    },
    "external_dependencies": {
        "python": [],
    },
    "license": "Other proprietary",
    "bootstrap": True,  # 加载登录屏幕的翻译，
}
