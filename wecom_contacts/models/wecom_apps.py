# -*- coding: utf-8 -*-

import logging
import time
from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons.wecom_api.api.wecom_abstract_api import ApiException

_logger = logging.getLogger(__name__)


class WeComApps(models.Model):
    _inherit = "wecom.apps"

    def cron_get_app_jsapi_ticket(self):
        """
        定时任务，每隔两小时更新应用的jsapi_ticket
        """
        for app in self:
            if (
                app.company_id.is_wecom_organization
                and app.company_id.corpid
                and app.secret
            ):
                _logger.info(
                    _("Automatic tasks:Start getting JSAPI ticket for app [%s]")
                    % (app.name)
                )
                if (
                    app.jsapi_ticket_expiration_time
                    and app.jsapi_ticket_expiration_time > datetime.now()
                ):
                    _logger.info(
                        _(
                            "Automatic tasks:JSAPI ticket for app [%s] is not expired, no need to update"
                        )
                        % (app.name)
                    )
                else:
                    try:
                        wecom_api = self.env["wecom.service_api"].InitServiceApi(
                            app.company_id.corpid, app.secret
                        )
                        response = wecom_api.httpCall(
                            self.env["wecom.service_api_list"].get_server_api_call(
                                "AGENT_GET_TICKET"
                            ),
                            {"type": "agent_config"},
                        )
                    except ApiException as e:
                        _logger.error(
                            _(
                                "Automatic tasks:Failed to get JSAPI ticket for app [%s], error: %s"
                            )
                            % (app.name, e)
                        )
                    else:
                        if response["errcode"] == 0:
                            app.write(
                                {
                                    "jsapi_ticket": response["ticket"],
                                    "jsapi_ticket_expiration_time": datetime.now()
                                    + timedelta(seconds=response["expires_in"]),
                                }
                            )
                    _logger.info(
                        _("Automatic tasks:Successfully get JSAPI ticket for app [%s]")
                        % (app.name)
                    )
            _logger.info(
                _("Automatic tasks:Start getting app [%s] ticket for company [%s]")
                % (app.name, app.company_id.name)
            )
