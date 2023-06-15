# -*- coding: utf-8 -*-
{
    "name": "WeCom Material",
    "author": "RStudio",
    "website": "https://eis-solution.coding.net/public/odoo/oec/git",
    "sequence": 604,
    "installable": True,
    "application": True,
    "auto_install": False,
    "category": "WeCom Suites/Material",
    "version": "16.0.0.1",
    "summary": """
        WeCom material management
        """,
    "description": """
please make sure ffmpeg, sox, and mediainfo are installed on your system, e.g.

DOC:
=============

* https://github.com/jiaaro/pydub

Install:
=============

::

    # libav
    apt-get install libav-tools libavcodec-extra

    # ffmpeg
    apt-get install ffmpeg libavcodec-extra

    # pydub
    pip install pydub ffmpy
    or
    pip3 install pydub ffmpy

""",
    "depends": ["attachment_indexation", "wecom_contacts"],
    "data": [
        "security/wecom_material_security.xml",
        "security/ir.model.access.csv",
        "data/wecom_apps_data.xml",
        "data/material_data.xml",
        "views/material_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {},
    "external_dependencies": {
        "python": ["ffmpy", "pydub", "requests_toolbelt"],
    },
    "pre_init_hook": "pre_init_hook",
    "license": "AGPL-3",
}
