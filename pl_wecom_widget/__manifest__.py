# -*- coding: utf-8 -*-

{
    "name": "Pl WeCom Widget",
    "author": "PL,RStudio",
    "category": "WeCom/WeCom",
    "summary": "WeCom Widget",
    "website": "https://github.com/odoochain",
    "version": "14.0.0.4",
    "description": """ 

""",
    "depends": [
        "web",
    ],
    "data": [
            "views/assets_templates.xml",
    ],
    'qweb': [
        'static/src/xml/*.xml',
        'static/src/legacy/js/week_days.js',
    ],
    "sequence": 600,
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "LGPL-3",
}
