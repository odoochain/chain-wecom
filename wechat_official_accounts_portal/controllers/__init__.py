# -*- coding: utf-8 -*-

from . import main


# -*- coding: utf-8 -*-

# !参考 \addons\auth_oauth\controllers\main.py
import time
import requests  # type: ignore
import logging
import json
import werkzeug.urls  # type: ignore
import werkzeug.utils  # type: ignore
from urllib.parse import urlparse, urlencode
from werkzeug.exceptions import BadRequest  # type: ignore

from odoo import api, http, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, ValidationError, UserError
from odoo.http import request, Response
from odoo import registry as registry_get
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home  # type: ignore
from odoo.addons.auth_oauth.controllers.main import fragment_to_query_string  # type: ignore
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url  # type: ignore
from odoo.addons.wechat_api.tools.security import WeChatApiToolsSecurity  # type: ignore

_logger = logging.getLogger(__name__)
